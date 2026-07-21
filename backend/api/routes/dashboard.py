"""
Dashboard endpoints — read-only data feeds for the React frontend. These
call the analytics engine DIRECTLY, not through agents, because rendering a
grid of numbers doesn't need an LLM in the loop; only the copilot chat does.

Response shapes are deliberately mapped to the names the frontend TypeScript
types expect:
  - usable_qty          → usable_inventory
  - safety_stock_qty    → safety_stock
  - reorder_point_qty   → reorder_point
  - max_stock_qty       → max_stock
  - rationale           → reason
  - total_material_plant_rows → total_rows
  - material detail is flattened (health/projection/impact/coverage merged)
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from data.repository import get_repository
from analytics.health_classification import get_material_health, get_all_material_health
from analytics.priority_scoring import rank_at_risk_materials, score_material
from analytics.production_impact import get_production_impact
from analytics.projection import project_material_balance
from analytics.po_analysis import analyze_po_coverage
from analytics.replenishment import draft_recommendations, recommend_for_material
from analytics.inventory_calc import get_days_of_supply
from analytics.product_bom_risk import get_product_risk, get_products_for_material
from models.schemas import ProductRiskRow, ProductBomRiskRow, MaterialUsageRow


router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _health_to_row(h) -> dict:
    """Map a MaterialHealth object to the flat shape the frontend expects."""
    return {
        "material_id": h.material_id,
        "plant_id": h.plant_id,
        "status": h.status,
        "reason": h.reason,
        "usable_inventory": h.usable_qty,
        "safety_stock": h.safety_stock_qty,
        "reorder_point": h.reorder_point_qty,
        "max_stock": h.max_stock_qty,
    }


def _rec_to_row(r) -> dict:
    """Map a ReplenishmentRecommendation to the shape the frontend expects."""
    return {
        "material_id": r.material_id,
        "plant_id": r.plant_id,
        "recommended_action": r.recommended_action,
        "recommended_qty": r.recommended_qty,
        "suggested_supplier_id": r.suggested_supplier_id,
        "lead_time_days": r.lead_time_days,
        "priority": r.priority_score,          # frontend reads 'priority'
        "priority_score": r.priority_score,    # keep raw score too
        "reason": r.rationale,                 # frontend reads 'reason'
    }


@router.get("/summary")
def summary():
    repo = get_repository()
    all_health = get_all_material_health(repo)
    counts: dict[str, int] = {}
    for h in all_health:
        counts[h.status] = counts.get(h.status, 0) + 1
    total = len(all_health)
    return {
        "total_rows": total,                        # frontend reads total_rows
        "total_material_plant_rows": total,         # keep original key for compat
        "status_counts": counts,
    }


@router.get("/product-risk", response_model=list[ProductRiskRow])
def product_risk(plant_id: str | None = None, health_status: str | None = None):
    repo = get_repository()
    rows = []
    for (material_id, plant_id_key), policy in repo.policy_by_key.items():
        if plant_id and plant_id_key != plant_id:
            continue
        health = get_material_health(repo, material_id, plant_id_key)
        if not health:
            continue
        if health_status and health.status != health_status:
            continue
        material = repo.material_by_id.get(material_id)
        material_name = material.material_name if material else material_id
        
        days_supply = get_days_of_supply(repo, material_id, plant_id_key)
        score = score_material(repo, material_id, plant_id_key)
        
        rows.append(ProductRiskRow(
            material_id=material_id,
            material_name=material_name,
            plant_id=plant_id_key,
            on_hand_qty=health.usable_qty,
            safety_stock=health.safety_stock_qty,
            reorder_point=health.reorder_point_qty,
            max_stock=health.max_stock_qty,
            health_status=health.status,
            days_of_supply=days_supply,
            priority_score=score
        ))
    
    # Sort by priority score descending
    rows.sort(key=lambda x: x.priority_score, reverse=True)
    return rows


@router.get("/product-bom-risk", response_model=list[ProductBomRiskRow])
def product_bom_risk(plant_id: str | None = None, health_status: str | None = None):
    """Return product BOM risk rows.

    Default behaviour (no plant_id): each product is evaluated at its own
    primary_plant_id only.  Pass plant_id to override and see a specific plant,
    or plant_id=all to see every product × every plant combination.

    health_status is an optional filter applied on top — pass e.g.
    health_status=Shortage to see only at-risk rows.
    """
    repo = get_repository()
    rows = []

    for product in repo.products:
        # Determine which plant(s) to evaluate for this product
        if plant_id and plant_id != "all":
            plants_to_check = [plant_id]
        elif plant_id == "all":
            plants_to_check = [p.plant_id for p in repo.plants]
        else:
            # Default: primary plant only — avoids flooding the view with
            # cross-plant rows where most BOM components have no local stock
            plants_to_check = [product.primary_plant_id]

        for pid in plants_to_check:
            risk_row = get_product_risk(repo, product.product_id, pid)
            if not risk_row:
                continue
            if health_status and risk_row.risk_status != health_status:
                continue
            rows.append(risk_row)

    # Sort by priority score descending
    rows.sort(key=lambda x: x.priority_score, reverse=True)
    return rows


@router.get("/materials")
def materials(status: str | None = None, risky_only: bool = False, top_n: int = 100):
    repo = get_repository()
    if risky_only:
        at_risk_statuses = {"Shortage", "Safety Stock Warning", "Near Reorder"}
        results = [
            r for r in get_all_material_health(repo, status_filter=status)
            if r.status in at_risk_statuses
        ]
    else:
        results = get_all_material_health(repo, status_filter=status)
    return [_health_to_row(r) for r in results[:top_n]]


@router.get("/materials/{material_id}/{plant_id}")
def material_detail(material_id: str, plant_id: str):
    repo = get_repository()
    health = get_material_health(repo, material_id, plant_id)
    if health is None:
        raise HTTPException(404, f"No policy found for {material_id} at {plant_id}")

    impact = get_production_impact(repo, material_id, plant_id)
    projection = project_material_balance(repo, material_id, plant_id, horizon_days=30)
    coverage = analyze_po_coverage(repo, material_id, plant_id)

    # Flat response — frontend reads fields directly off the top-level object
    return {
        # health fields
        "material_id": health.material_id,
        "plant_id": health.plant_id,
        "status": health.status,
        "reason": health.reason,
        "usable_inventory": health.usable_qty,
        "safety_stock": health.safety_stock_qty,
        "reorder_point": health.reorder_point_qty,
        "max_stock": health.max_stock_qty,
        # projection fields
        "projected_shortage_date": str(projection.shortage_date) if projection.shortage_date else None,
        "projected_shortage_qty": projection.shortage_qty,
        "starting_balance": projection.starting_balance,
        # nested objects (displayed as JSON cards in the UI)
        "production_impact": impact.model_dump(),
        "po_coverage": coverage.model_dump(),
    }


@router.get("/priority")
def priority(top_n: int = 20):
    repo = get_repository()
    return rank_at_risk_materials(repo, top_n=top_n)


@router.get("/recommendations")
def recommendations(top_n: int = 20):
    repo = get_repository()
    return [_rec_to_row(r) for r in draft_recommendations(repo, top_n=top_n)]


@router.get("/recommendations/{material_id}/{plant_id}")
def recommendation_detail(material_id: str, plant_id: str):
    repo = get_repository()
    rec = recommend_for_material(repo, material_id, plant_id)
    if rec is None:
        raise HTTPException(404, f"No recommendation available for {material_id} at {plant_id}")
    return _rec_to_row(rec)


@router.get("/material-usage/{material_id}", response_model=list[MaterialUsageRow])
def material_usage(material_id: str, plant_id: str | None = None):
    repo = get_repository()
    return get_products_for_material(repo, material_id, plant_id)


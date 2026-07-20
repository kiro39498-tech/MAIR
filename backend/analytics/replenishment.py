"""
Replenishment recommendation engine. Phase 1 scope: DRAFT ONLY — this module
produces a recommendation object; nothing here places an order or writes to
any external system. Execution (writing back to source systems) is a
deliberately separate, later phase — see the architecture doc's
draft -> notify -> approve -> execute flow.
"""
from __future__ import annotations

from data.repository import Repository
from models.schemas import ReplenishmentRecommendation
from analytics.health_classification import get_material_health
from analytics.po_analysis import analyze_po_coverage
from analytics.priority_scoring import score_material
from analytics.inventory_calc import get_inventory_across_plants


def _pick_supplier(repo: Repository, material_id: str, prefer_fast: bool = False):
    options = repo.supplier_materials_by_material.get(material_id, [])
    if not options:
        return None
    if prefer_fast:
        return min(options, key=lambda s: s.lead_time_days)
    primary = [s for s in options if s.is_primary_supplier]
    return primary[0] if primary else options[0]


def _check_transfer_option(repo: Repository, material_id: str, plant_id: str, shortfall: float):
    """Look for surplus of the same material at another plant — a transfer
    can be faster than a new PO."""
    for snap in get_inventory_across_plants(repo, material_id):
        if snap.plant_id == plant_id:
            continue
        policy = repo.policy_by_key.get((material_id, snap.plant_id))
        if policy and snap.usable_qty - policy.safety_stock_qty >= shortfall:
            return snap.plant_id, snap.usable_qty - policy.safety_stock_qty
    return None, None


def recommend_for_material(repo: Repository, material_id: str, plant_id: str) -> ReplenishmentRecommendation | None:
    health = get_material_health(repo, material_id, plant_id)
    if health is None:
        return None

    priority = score_material(repo, material_id, plant_id)
    coverage = analyze_po_coverage(repo, material_id, plant_id)
    policy = repo.policy_by_key.get((material_id, plant_id))
    if not policy:
        return None

    supplier = _pick_supplier(repo, material_id, prefer_fast=(health.status == "Shortage"))
    lead_time = supplier.lead_time_days if supplier else 0
    adjusted_rop = policy.avg_daily_usage * lead_time + policy.safety_stock_qty
    
    usable_qty = health.usable_qty
    shortfall = max(adjusted_rop - usable_qty, 0)
    days_of_supply = round(usable_qty / policy.avg_daily_usage, 1) if policy.avg_daily_usage > 0 else 999.0

    # 1. Usable stock is healthy/above lead-time-adjusted ROP — no action needed.
    if shortfall <= 0:
        return ReplenishmentRecommendation(
            material_id=material_id, plant_id=plant_id,
            recommended_action="Monitor", priority_score=priority,
            lead_time_days=lead_time,
            rationale=(
                f"On-hand {usable_qty:.0f} units vs. reorder point {adjusted_rop:.0f} units (lead-time adjusted); "
                f"{days_of_supply} days of supply remaining vs. {lead_time}-day lead time. Stock level is healthy."
            ),
        )

    open_po_qty = coverage.open_po_qty
    net_shortfall = max(shortfall - open_po_qty, 0)

    # 2. Outstanding POs cover the shortfall (both quantity and timing).
    if net_shortfall <= 0 and coverage.covers_shortfall:
        if coverage.has_late_po:
            return ReplenishmentRecommendation(
                material_id=material_id, plant_id=plant_id,
                recommended_action="Expedite", recommended_qty=open_po_qty,
                lead_time_days=lead_time,
                priority_score=priority,
                rationale=(
                    f"On-hand {usable_qty:.0f} units vs. reorder point {adjusted_rop:.0f} units (lead-time adjusted); "
                    f"{days_of_supply} days of supply remaining vs. {lead_time}-day lead time. "
                    f"An open PO of {open_po_qty:.0f} units covers the shortfall but is late. Recommend expediting."
                ),
            )
        else:
            return ReplenishmentRecommendation(
                material_id=material_id, plant_id=plant_id,
                recommended_action="Monitor", priority_score=priority,
                lead_time_days=lead_time,
                rationale=(
                    f"On-hand {usable_qty:.0f} units vs. reorder point {adjusted_rop:.0f} units (lead-time adjusted); "
                    f"{days_of_supply} days of supply remaining vs. {lead_time}-day lead time. "
                    f"An open PO of {open_po_qty:.0f} units is on-time and covers the shortfall."
                ),
            )

    # If timing is not covered or there is still a net shortfall, we act:
    transfer_needed = net_shortfall if net_shortfall > 0 else shortfall

    # 3. Same-material surplus at another plant is faster than a new PO.
    donor_plant, available = _check_transfer_option(repo, material_id, plant_id, transfer_needed)
    if donor_plant:
        return ReplenishmentRecommendation(
            material_id=material_id, plant_id=plant_id,
            recommended_action="Transfer", recommended_qty=int(transfer_needed),
            lead_time_days=lead_time,
            priority_score=priority,
            rationale=(
                f"On-hand {usable_qty:.0f} units vs. reorder point {adjusted_rop:.0f} units (lead-time adjusted); "
                f"{days_of_supply} days of supply remaining vs. {lead_time}-day lead time; "
                f"open PO of {open_po_qty:.0f} units is {'late' if coverage.has_late_po else 'insufficient'} (net shortfall {net_shortfall:.0f} units). "
                f"Plant {donor_plant} has {available:.0f} units of surplus above safety stock; recommend transferring {transfer_needed:.0f} units."
            ),
        )

    # 4. Purchase order creation (Replenish / Restore Safety Stock)
    base_qty = max(policy.reorder_qty, net_shortfall)
    moq = supplier.moq if supplier else 0
    
    if supplier:
        if base_qty <= moq:
            recommended_qty = moq
        else:
            recommended_qty = ((int(base_qty) + moq - 1) // moq) * moq
    else:
        recommended_qty = int(base_qty)

    action = "Restore Safety Stock" if usable_qty < policy.safety_stock_qty else "Replenish"
    
    rationale_str = (
        f"On-hand {usable_qty:.0f} units vs. reorder point {adjusted_rop:.0f} units (lead-time adjusted); "
        f"{days_of_supply} days of supply remaining vs. {lead_time}-day lead time; "
        f"open PO of {open_po_qty:.0f} units is insufficient (net shortfall {net_shortfall:.0f} units). "
        f"Recommend ordering {recommended_qty} units"
    )
    if supplier:
        rationale_str += f" from supplier {supplier.supplier_id} (MOQ {moq} units)."
    else:
        rationale_str += "."

    return ReplenishmentRecommendation(
        material_id=material_id, plant_id=plant_id,
        recommended_action=action,
        recommended_qty=recommended_qty,
        suggested_supplier_id=supplier.supplier_id if supplier else None,
        lead_time_days=lead_time,
        priority_score=priority,
        rationale=rationale_str,
    )



def draft_recommendations(repo: Repository, top_n: int = 20) -> list[ReplenishmentRecommendation]:
    """Phase 1 entry point for the Replenishment Agent: top-N at-risk
    materials, each with a drafted (not executed) recommendation."""
    from analytics.priority_scoring import rank_at_risk_materials
    ranked = rank_at_risk_materials(repo, top_n=top_n)
    out = []
    for r in ranked:
        rec = recommend_for_material(repo, r["material_id"], r["plant_id"])
        if rec:
            out.append(rec)
    return out

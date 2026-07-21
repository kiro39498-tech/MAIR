from __future__ import annotations
from data.repository import Repository
from models.schemas import ProductBomRiskRow, BlockingComponent, BomComponent, MaterialUsageRow
from analytics.health_classification import get_material_health
from analytics.priority_scoring import score_material

# Status weights for worst-case roll-up
_STATUS_WEIGHTS: dict[str, int] = {
    "Shortage": 4,
    "Safety Stock Warning": 3,
    "Near Reorder": 2,
    "Excess": 1,
    "Healthy": 0,
}
_BLOCKING_STATUSES = frozenset({"Shortage", "Safety Stock Warning", "Near Reorder"})


def get_product_risk(repo: Repository, product_id: str, plant_id: str) -> ProductBomRiskRow | None:
    """Explode product BOM and determine rolled-up risk status using worst-case logic.

    Roll-up priority (highest wins):
      Shortage > Safety Stock Warning > Near Reorder > Excess > Healthy

    Returns a row for every product that has BOM lines, even if the rolled-up
    status is Healthy or Excess.  A None return means the product has *no* BOM
    entries at all (i.e. it is not manufactured from tracked components).

    all_components contains every BOM line with its current health at this
    plant.  Components whose material has no inventory policy at this plant are
    included with has_inventory_data=False and health_status="No Data".

    blocking_components is the legacy subset used by the outer table's
    "blocker count" badge — it contains only Shortage / Safety Stock Warning /
    Near Reorder entries.
    """
    bom_lines = repo.bom_by_product.get(product_id, [])
    if not bom_lines:
        return None

    blocking_components: list[BlockingComponent] = []
    all_components: list[BomComponent] = []
    statuses: list[str] = []

    worst_status = "Healthy"
    worst_weight = 0

    for line in bom_lines:
        health = get_material_health(repo, line.material_id, plant_id)
        material = repo.material_by_id.get(line.material_id)
        material_name = material.material_name if material else line.material_id

        if not health:
            # Component exists in the BOM but has no policy/inventory at this
            # plant.  Show it in the full BOM view so operators can see the gap.
            all_components.append(BomComponent(
                material_id=line.material_id,
                material_name=material_name,
                health_status="No Data",
                usable_qty=0.0,
                reorder_point=0.0,
                safety_stock=0.0,
                qty_per_unit=line.quantity_per_unit,
                net_shortfall=0.0,
                is_blocking=False,
                has_inventory_data=False,
            ))
            continue

        status = health.status
        statuses.append(status)
        weight = _STATUS_WEIGHTS.get(status, 0)
        is_blocking = status in _BLOCKING_STATUSES
        shortfall = max(health.reorder_point_qty - health.usable_qty, 0.0)

        all_components.append(BomComponent(
            material_id=line.material_id,
            material_name=material_name,
            health_status=status,
            usable_qty=health.usable_qty,
            reorder_point=health.reorder_point_qty,
            safety_stock=health.safety_stock_qty,
            qty_per_unit=line.quantity_per_unit,
            net_shortfall=shortfall if is_blocking else 0.0,
            is_blocking=is_blocking,
            has_inventory_data=True,
        ))

        if is_blocking:
            blocking_components.append(BlockingComponent(
                material_id=line.material_id,
                health_status=status,
                usable_qty=health.usable_qty,
                reorder_point=health.reorder_point_qty,
                safety_stock=health.safety_stock_qty,
                shortfall=shortfall,
            ))

        if weight > worst_weight:
            worst_weight = weight
            worst_status = status

    # If we only saw "No Data" components, statuses is empty — still return
    # the row so operators can see the product has unmapped BOM entries.
    if not statuses and not all_components:
        return None

    if worst_weight == 0 and "Excess" in statuses:
        worst_status = "Excess"

    # Sort all_components: blockers first (by descending weight), then the rest
    all_components.sort(
        key=lambda c: (_STATUS_WEIGHTS.get(c.health_status, -1), c.net_shortfall),
        reverse=True,
    )

    # Priority score = max priority score of any blocking component
    max_priority = 0.0
    for block in blocking_components:
        c_score = score_material(repo, block.material_id, plant_id)
        if c_score > max_priority:
            max_priority = c_score

    product = repo.product_by_id.get(product_id)
    product_name = product.product_name if product else product_id

    return ProductBomRiskRow(
        product_id=product_id,
        product_name=product_name,
        plant_id=plant_id,
        risk_status=worst_status,
        blocking_components=blocking_components,
        all_components=all_components,
        priority_score=max_priority,
    )


def get_products_for_material(
    repo: Repository, material_id: str, plant_id: str | None = None
) -> list[MaterialUsageRow]:
    """Find every finished product whose BOM uses this material.
    
    If plant_id is provided, limit the search to that plant.
    """
    bom_lines = repo.products_using_material(material_id)
    if not bom_lines:
        return []

    # Map product_id to quantity_per_unit (worst case or last BOM line)
    product_qtys = {}
    for line in bom_lines:
        product_qtys[line.product_id] = line.quantity_per_unit

    results = []
    plants_to_check = [plant_id] if plant_id else [p.plant_id for p in repo.plants]

    for prod_id, qty_per_unit in product_qtys.items():
        product = repo.product_by_id.get(prod_id)
        product_name = product.product_name if product else prod_id

        for p_id in plants_to_check:
            risk_row = get_product_risk(repo, prod_id, p_id)
            if not risk_row:
                continue

            # This material is blocking if it appears in the product's blocking_components
            is_blocking = any(bc.material_id == material_id for bc in risk_row.blocking_components)

            results.append(MaterialUsageRow(
                product_id=prod_id,
                product_name=product_name,
                plant_id=p_id,
                risk_status=risk_row.risk_status,
                qty_per_unit=qty_per_unit,
                is_blocking=is_blocking
            ))

    # Sort results by product_id for predictability
    results.sort(key=lambda x: (x.product_id, x.plant_id))
    return results


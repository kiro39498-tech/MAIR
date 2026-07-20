from __future__ import annotations
from data.repository import Repository
from models.schemas import ProductBomRiskRow, BlockingComponent
from analytics.health_classification import get_material_health
from analytics.priority_scoring import score_material

def get_product_risk(repo: Repository, product_id: str, plant_id: str) -> ProductBomRiskRow | None:
    """Explode product BOM and determine rolled up risk status using worst-case logic.
    - If any component is Shortage -> product is Shortage
    - Else if any component is Safety Stock Warning -> Safety Stock Warning
    - Else if any component is Near Reorder -> Near Reorder
    - Else if any component is Excess -> Excess
    - Else Healthy
    """
    bom_lines = repo.bom_by_product.get(product_id, [])
    if not bom_lines:
        return None

    blocking_components = []
    statuses = []

    status_weights = {
        "Shortage": 4,
        "Safety Stock Warning": 3,
        "Near Reorder": 2,
        "Excess": 1,
        "Healthy": 0,
    }

    worst_status = "Healthy"
    worst_weight = 0

    for line in bom_lines:
        health = get_material_health(repo, line.material_id, plant_id)
        if not health:
            continue

        status = health.status
        statuses.append(status)
        weight = status_weights.get(status, 0)

        # Calculate shortfall for component
        shortfall = max(health.reorder_point_qty - health.usable_qty, 0.0)

        # Components with risk statuses are blocking components
        if status in ("Shortage", "Safety Stock Warning", "Near Reorder"):
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

    if not statuses:
        return None

    if worst_weight == 0 and "Excess" in statuses:
        worst_status = "Excess"

    # Set priority score as the maximum priority score of any blocker
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
        priority_score=max_priority,
    )

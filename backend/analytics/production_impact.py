"""
Production impact — maps a constrained material to the production orders it
threatens, via the BOM. This is what lets the system say "this shortage
blocks 3 production orders worth 480 units due in the next 2 weeks"
instead of just "this material is low."
"""
from __future__ import annotations

from data.repository import Repository
from models.schemas import ProductionImpact
from analytics.bom_explosion import products_using_material


def get_production_impact(repo: Repository, material_id: str, plant_id: str) -> ProductionImpact:
    affected_products = set(products_using_material(repo, material_id))
    affected_orders = []
    total_qty_at_risk = 0
    due_dates = []

    for po in repo.production_orders:
        if po.plant_id != plant_id or po.status not in ("Released", "In Process", "Confirmed", "Delayed"):
            continue
        if po.product_id in affected_products:
            affected_orders.append(po.production_order_id)
            total_qty_at_risk += po.order_qty
            due_dates.append(po.due_date)

    n = len(affected_orders)
    severity = "High" if n >= 3 else "Medium" if n >= 1 else "Low"

    return ProductionImpact(
        material_id=material_id,
        plant_id=plant_id,
        affected_production_orders=affected_orders,
        total_qty_at_risk=total_qty_at_risk,
        earliest_due_date=min(due_dates) if due_dates else None,
        impact_severity=severity,
    )

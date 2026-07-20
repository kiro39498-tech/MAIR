"""
Time-phased inventory projection. Walks forward day-by-day from the current
usable balance, subtracting dated demand (from production orders exploded
through the BOM, plus forecast) and adding dated supply (open PO receipts),
to find the first date the projected balance goes negative.
"""
from __future__ import annotations

from datetime import date, timedelta
from collections import defaultdict

from data.repository import Repository
from models.schemas import MaterialProjection, ProjectionPoint
from analytics.inventory_calc import get_usable_inventory
from analytics.bom_explosion import explode_product_qty

DEFAULT_HORIZON_DAYS = 60


def _dated_demand(repo: Repository, material_id: str, plant_id: str, horizon_days: int) -> dict[date, float]:
    demand: dict[date, float] = defaultdict(float)
    for po in repo.production_orders:
        if po.plant_id != plant_id or po.status not in ("Released", "In Process", "Confirmed", "Delayed"):
            continue
        material_qty = explode_product_qty(repo, po.product_id, po.order_qty).get(material_id)
        if material_qty:
            demand[po.due_date] += material_qty
    return demand


def _dated_supply(repo: Repository, material_id: str, plant_id: str) -> dict[date, float]:
    supply: dict[date, float] = defaultdict(float)
    for po in repo.open_pos_by_material_plant.get((material_id, plant_id), []):
        supply[po.expected_receipt_date] += po.open_qty
    return supply


def project_material_balance(
    repo: Repository, material_id: str, plant_id: str, horizon_days: int = DEFAULT_HORIZON_DAYS
) -> MaterialProjection:
    starting_balance = get_usable_inventory(repo, material_id, plant_id)
    demand_by_date = _dated_demand(repo, material_id, plant_id, horizon_days)
    supply_by_date = _dated_supply(repo, material_id, plant_id)

    today = date.today()
    balance = starting_balance
    points: list[ProjectionPoint] = []
    shortage_date, shortage_qty = None, None

    for offset in range(horizon_days + 1):
        d = today + timedelta(days=offset)
        demand_qty = demand_by_date.get(d, 0.0)
        supply_qty = supply_by_date.get(d, 0.0)
        balance = balance - demand_qty + supply_qty
        points.append(ProjectionPoint(date=d, projected_balance=balance, demand_qty=demand_qty, supply_qty=supply_qty))
        if balance < 0 and shortage_date is None:
            shortage_date = d
            shortage_qty = abs(balance)

    return MaterialProjection(
        material_id=material_id,
        plant_id=plant_id,
        starting_balance=starting_balance,
        points=points,
        shortage_date=shortage_date,
        shortage_qty=shortage_qty,
    )

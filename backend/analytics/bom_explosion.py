"""
BOM explosion — converts a product-level quantity into per-material demand.
Pure lookup/arithmetic over the canonical BOM, no AI.
"""
from __future__ import annotations

from collections import defaultdict

from data.repository import Repository


def explode_product_qty(repo: Repository, product_id: str, qty: float) -> dict[str, float]:
    """Return {material_id: required_qty} for producing `qty` units of `product_id`."""
    demand: dict[str, float] = {}
    for line in repo.bom_by_product.get(product_id, []):
        demand[line.material_id] = demand.get(line.material_id, 0.0) + line.quantity_per_unit * qty
    return demand


def explode_production_orders(repo: Repository, plant_id: str | None = None) -> dict[str, float]:
    """Aggregate material demand across all open production orders (optionally
    filtered to one plant). This is the raw material-demand signal used by
    the projection engine."""
    total: dict[str, float] = defaultdict(float)
    for po in repo.production_orders:
        if po.status not in ("Released", "In Process", "Confirmed", "Delayed"):
            continue
        if plant_id and po.plant_id != plant_id:
            continue
        for material_id, qty in explode_product_qty(repo, po.product_id, po.order_qty).items():
            total[material_id] += qty
    return dict(total)


def materials_used_by_product(repo: Repository, product_id: str) -> list[str]:
    return [line.material_id for line in repo.bom_by_product.get(product_id, [])]


def products_using_material(repo: Repository, material_id: str) -> list[str]:
    """The reverse mapping — needed by the Production Impact Agent to find
    every product a constrained material feeds into."""
    return list({line.product_id for line in repo.bom_by_material.get(material_id, [])})

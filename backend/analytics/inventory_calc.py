"""
Inventory calculation — the single source of truth for "usable" quantity.
Every other analytics module calls this instead of reading raw inventory
fields itself, so the usable-inventory definition only lives in one place.
"""
from __future__ import annotations

from data.repository import Repository
from models.schemas import InventorySnapshot


def get_usable_inventory(repo: Repository, material_id: str, plant_id: str) -> float:
    """Usable inventory = unrestricted stock minus what's already reserved
    against open production orders. Quality-hold and blocked stock are
    on-hand but excluded — they are not available to fulfil demand."""
    snap = repo.inventory_by_key.get((material_id, plant_id))
    if snap is None:
        return 0.0
    return snap.usable_qty


def get_inventory_snapshot(repo: Repository, material_id: str, plant_id: str) -> InventorySnapshot | None:
    return repo.inventory_by_key.get((material_id, plant_id))


def get_inventory_across_plants(repo: Repository, material_id: str) -> list[InventorySnapshot]:
    """All plants a material is stocked at — needed for inter-plant
    redistribution comparisons."""
    return [i for i in repo.inventory if i.material_id == material_id]


def get_days_of_supply(repo: Repository, material_id: str, plant_id: str) -> float:
    """Usable inventory divided by avg daily usage."""
    usable = get_usable_inventory(repo, material_id, plant_id)
    policy = repo.policy_by_key.get((material_id, plant_id))
    if not policy or policy.avg_daily_usage <= 0:
        return 9999.0
    return round(usable / policy.avg_daily_usage, 2)


"""
Inventory Domain Repository.
Reads inventory snapshots and policies via BaseConnector.
"""
from __future__ import annotations

from typing import List, Dict, Tuple
from connectors.base import BaseConnector
from models.canonical import InventorySnapshot, InventoryPolicy, Plant, Warehouse


class InventoryRepository:
    def __init__(self, connector: BaseConnector):
        self.connector = connector
        self.inventory: List[InventorySnapshot] = self.connector.get_inventory()
        self.policies: List[InventoryPolicy] = self.connector.get_inventory_policies()
        self.plants: List[Plant] = self.connector.get_plants()
        self.warehouses: List[Warehouse] = self.connector.get_warehouses()

        self.inventory_by_key: Dict[Tuple[str, str], InventorySnapshot] = {
            (inv.material_id, inv.plant_id): inv for inv in self.inventory
        }
        self.policy_by_key: Dict[Tuple[str, str], InventoryPolicy] = {
            (p.material_id, p.plant_id): p for p in self.policies
        }
        self.plant_by_id: Dict[str, Plant] = {p.plant_id: p for p in self.plants}

    def get_inventory_for_key(self, material_id: str, plant_id: str) -> InventorySnapshot | None:
        return self.inventory_by_key.get((material_id, plant_id))

    def get_policy_for_key(self, material_id: str, plant_id: str) -> InventoryPolicy | None:
        return self.policy_by_key.get((material_id, plant_id))

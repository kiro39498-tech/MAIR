"""
Purchase Orders & Manager Approval Domain Repository.
"""
from __future__ import annotations

from collections import defaultdict
from typing import List, Dict, Tuple
from connectors.base import BaseConnector
from models.canonical import PurchaseOrder, Manager, InventoryTransaction


class PurchaseRepository:
    def __init__(self, connector: BaseConnector):
        self.connector = connector
        self.purchase_orders: List[PurchaseOrder] = self.connector.get_purchase_orders()
        self.inventory_transactions: List[InventoryTransaction] = self.connector.get_inventory_transactions()
        self.managers: List[Manager] = self.connector.get_managers()

        self.open_pos_by_material_plant: Dict[Tuple[str, str], List[PurchaseOrder]] = defaultdict(list)
        for po in self.purchase_orders:
            if po.status in ("Open", "Partially Received", "Late"):
                self.open_pos_by_material_plant[(po.material_id, po.plant_id)].append(po)

        self.managers_by_plant: Dict[str, List[Manager]] = defaultdict(list)
        for mgr in self.managers:
            self.managers_by_plant[mgr.plant_id].append(mgr)

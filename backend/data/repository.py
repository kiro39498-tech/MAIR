"""
In-memory repository over the canonical model. This is the ONLY place
analytics code reads data from — it never touches a connector or a CSV path
directly. That indirection is what lets the connector be swapped later
without touching a single analytics function.
"""
from __future__ import annotations

from collections import defaultdict
from functools import lru_cache

from connectors.csv_connector import get_connector
from models.schemas import (
    Plant, Warehouse, Product, Material, BomLine, Supplier, SupplierMaterial,
    InventoryPolicy, InventorySnapshot, ProductionOrder, PurchaseOrder,
    DemandForecastLine, InventoryTransaction, Manager,
)


class Repository:
    def __init__(self):
        connector = get_connector()
        self.plants: list[Plant] = connector.get_plants()
        self.warehouses: list[Warehouse] = connector.get_warehouses()
        self.products: list[Product] = connector.get_products()
        self.materials: list[Material] = connector.get_materials()
        self.bom: list[BomLine] = connector.get_bom()
        self.suppliers: list[Supplier] = connector.get_suppliers()
        self.supplier_materials: list[SupplierMaterial] = connector.get_supplier_materials()
        self.inventory_policies: list[InventoryPolicy] = connector.get_inventory_policies()
        self.inventory: list[InventorySnapshot] = connector.get_inventory()
        self.production_orders: list[ProductionOrder] = connector.get_production_orders()
        self.purchase_orders: list[PurchaseOrder] = connector.get_purchase_orders()
        self.demand_forecast: list[DemandForecastLine] = connector.get_demand_forecast()
        self.inventory_transactions: list[InventoryTransaction] = connector.get_inventory_transactions()
        self.managers: list[Manager] = connector.get_managers()

        self._index()

    def _index(self) -> None:
        self.material_by_id = {m.material_id: m for m in self.materials}
        self.product_by_id = {p.product_id: p for p in self.products}
        self.plant_by_id = {p.plant_id: p for p in self.plants}
        self.supplier_by_id = {s.supplier_id: s for s in self.suppliers}

        self.policy_by_key = {(p.material_id, p.plant_id): p for p in self.inventory_policies}
        self.inventory_by_key = {(i.material_id, i.plant_id): i for i in self.inventory}

        self.bom_by_product: dict[str, list[BomLine]] = defaultdict(list)
        for line in self.bom:
            self.bom_by_product[line.product_id].append(line)

        self.bom_by_material: dict[str, list[BomLine]] = defaultdict(list)
        for line in self.bom:
            self.bom_by_material[line.material_id].append(line)

        self.supplier_materials_by_material: dict[str, list[SupplierMaterial]] = defaultdict(list)
        for sm in self.supplier_materials:
            self.supplier_materials_by_material[sm.material_id].append(sm)

        self.open_pos_by_material_plant: dict[tuple, list[PurchaseOrder]] = defaultdict(list)
        for po in self.purchase_orders:
            if po.status in ("Open", "Partially Received", "Late"):
                self.open_pos_by_material_plant[(po.material_id, po.plant_id)].append(po)

        self.production_orders_by_product_plant: dict[tuple, list[ProductionOrder]] = defaultdict(list)
        for po in self.production_orders:
            if po.status in ("Released", "In Process", "Confirmed", "Delayed"):
                self.production_orders_by_product_plant[(po.product_id, po.plant_id)].append(po)

        self.forecast_by_product_plant: dict[tuple, list[DemandForecastLine]] = defaultdict(list)
        for f in self.demand_forecast:
            self.forecast_by_product_plant[(f.product_id, f.plant_id)].append(f)

        self.managers_by_plant: dict[str, list[Manager]] = defaultdict(list)
        for mgr in self.managers:
            self.managers_by_plant[mgr.plant_id].append(mgr)


@lru_cache(maxsize=1)
def get_repository() -> Repository:
    """Singleton — the dataset is loaded once per process."""
    return Repository()

"""
CSV connector — Phase 1 data source, matches the generated dataset
(see /data/csv/data_dictionary.md for column definitions). Loads once,
caches in memory. Swap DATA_SOURCE to "sap"/"sql"/"fabric" later and
implement the equivalent connector; nothing else in the codebase changes.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

from connectors.base_connector import BaseConnector
from models.schemas import (
    Plant, Warehouse, ProductFamily, Product, Material, BomLine, Supplier,
    SupplierMaterial, InventoryPolicy, InventorySnapshot, ProductionOrder,
    PurchaseOrder, DemandForecastLine, InventoryTransaction, Manager,
)


class CsvConnector(BaseConnector):
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)

    def _read(self, filename: str) -> pd.DataFrame:
        path = self.data_dir / filename
        if not path.exists():
            raise FileNotFoundError(
                f"Expected dataset file not found: {path}. "
                f"Check CSV_DATA_DIR / csv_data_dir setting."
            )
        return pd.read_csv(path)

    def get_plants(self) -> list[Plant]:
        return [Plant(**r) for r in self._read("plants.csv").to_dict("records")]

    def get_warehouses(self) -> list[Warehouse]:
        return [Warehouse(**r) for r in self._read("warehouses.csv").to_dict("records")]

    def get_product_families(self) -> list[ProductFamily]:
        return [ProductFamily(**r) for r in self._read("product_families.csv").to_dict("records")]

    def get_products(self) -> list[Product]:
        return [Product(**r) for r in self._read("products.csv").to_dict("records")]

    def get_materials(self) -> list[Material]:
        return [Material(**r) for r in self._read("materials.csv").to_dict("records")]

    def get_bom(self) -> list[BomLine]:
        return [BomLine(**r) for r in self._read("bom.csv").to_dict("records")]

    def get_suppliers(self) -> list[Supplier]:
        df = self._read("suppliers.csv")
        df["preferred_supplier"] = df["preferred_supplier"] == "Y"
        return [Supplier(**r) for r in df.to_dict("records")]

    def get_supplier_materials(self) -> list[SupplierMaterial]:
        df = self._read("supplier_materials.csv")
        df["is_primary_supplier"] = df["is_primary_supplier"] == "Y"
        return [SupplierMaterial(**r) for r in df.to_dict("records")]

    def get_inventory_policies(self) -> list[InventoryPolicy]:
        return [InventoryPolicy(**r) for r in self._read("inventory_policies.csv").to_dict("records")]

    def get_inventory(self) -> list[InventorySnapshot]:
        return [InventorySnapshot(**r) for r in self._read("inventory.csv").to_dict("records")]

    def get_production_orders(self) -> list[ProductionOrder]:
        return [ProductionOrder(**r) for r in self._read("production_orders.csv").to_dict("records")]

    def get_purchase_orders(self) -> list[PurchaseOrder]:
        return [PurchaseOrder(**r) for r in self._read("purchase_orders.csv").to_dict("records")]

    def get_demand_forecast(self) -> list[DemandForecastLine]:
        df = self._read("demand_forecast.csv").rename(columns={})
        return [DemandForecastLine(**r) for r in df.to_dict("records")]

    def get_inventory_transactions(self) -> list[InventoryTransaction]:
        return [InventoryTransaction(**r) for r in self._read("inventory_transactions.csv").to_dict("records")]

    def get_managers(self) -> list[Manager]:
        return [Manager(**r) for r in self._read("managers.csv").to_dict("records")]


@lru_cache(maxsize=1)
def _cached_connector(data_dir: str) -> CsvConnector:
    return CsvConnector(data_dir)


def get_connector(data_dir: str | None = None) -> BaseConnector:
    """Factory — this is the one place that decides which connector is
    active. Analytics/repository code should call this, never instantiate
    CsvConnector directly, so switching DATA_SOURCE later is a one-line change."""
    from config.settings import settings
    return _cached_connector(data_dir or settings.csv_data_dir)

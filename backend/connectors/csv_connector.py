"""
Production CSV Connector — Phase 1 & 2 baseline dataset reader.
Integrates BaseConnector, Connector Registry, Mapping Engine, and Validation Engine.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import logging
import pandas as pd

from connectors.base import BaseConnector
from connectors.registry import register_connector
from connectors.mapping_engine import MappingEngine, get_default_mapping_dir
from connectors.validation_engine import ValidationEngine
from models.canonical import (
    Plant, Warehouse, ProductFamily, Product, Material, BomLine, Supplier,
    SupplierMaterial, InventoryPolicy, InventorySnapshot, ProductionOrder,
    PurchaseOrder, DemandForecastLine, InventoryTransaction, Manager, Batch, Reservation
)

logger = logging.getLogger(__name__)


@register_connector("csv", "csv_connector")
class CsvConnector(BaseConnector):
    """Production CSV connector reading tabular CSV files from a configured data directory."""

    def __init__(self, data_dir: str | Path, mapping_file: str | Path | None = None):
        self.data_dir = Path(data_dir)
        mapping_path = mapping_file or (get_default_mapping_dir() / "csv.json")
        self.mapping_engine = MappingEngine.load_from_file(mapping_path)

    def _read_records(self, entity_name: str, filename: str) -> list[dict]:
        path = self.data_dir / filename
        if not path.exists():
            raise FileNotFoundError(
                f"Expected dataset CSV file not found: {path}. "
                f"Check CSV_DATA_DIR setting."
            )
        df = pd.read_csv(path)
        # Replace NaN with default empty strings or None for pydantic safety
        df = df.where(pd.notnull(df), None)
        raw_records = df.to_dict("records")
        return self.mapping_engine.map_records(entity_name, raw_records)

    def load_plants(self) -> list[Plant]:
        records = self._read_records("plants", "plants.csv")
        valid, report = ValidationEngine.validate_records("plants", records, Plant)
        return [Plant(**r) for r in valid]

    def load_warehouses(self) -> list[Warehouse]:
        records = self._read_records("warehouses", "warehouses.csv")
        valid, report = ValidationEngine.validate_records("warehouses", records, Warehouse)
        return [Warehouse(**r) for r in valid]

    def load_product_families(self) -> list[ProductFamily]:
        records = self._read_records("product_families", "product_families.csv")
        valid, report = ValidationEngine.validate_records("product_families", records, ProductFamily)
        return [ProductFamily(**r) for r in valid]

    def load_products(self) -> list[Product]:
        records = self._read_records("products", "products.csv")
        valid, report = ValidationEngine.validate_records("products", records, Product)
        return [Product(**r) for r in valid]

    def load_materials(self) -> list[Material]:
        records = self._read_records("materials", "materials.csv")
        valid, report = ValidationEngine.validate_records("materials", records, Material)
        return [Material(**r) for r in valid]

    def load_bom(self) -> list[BomLine]:
        records = self._read_records("bom", "bom.csv")
        valid, report = ValidationEngine.validate_records("bom", records, BomLine)
        return [BomLine(**r) for r in valid]

    def load_suppliers(self) -> list[Supplier]:
        records = self._read_records("suppliers", "suppliers.csv")
        for r in records:
            if "preferred_supplier" in r and isinstance(r["preferred_supplier"], str):
                r["preferred_supplier"] = r["preferred_supplier"].upper() == "Y"
        valid, report = ValidationEngine.validate_records("suppliers", records, Supplier)
        return [Supplier(**r) for r in valid]

    def load_supplier_materials(self) -> list[SupplierMaterial]:
        records = self._read_records("supplier_materials", "supplier_materials.csv")
        for r in records:
            if "is_primary_supplier" in r and isinstance(r["is_primary_supplier"], str):
                r["is_primary_supplier"] = r["is_primary_supplier"].upper() == "Y"
        valid, report = ValidationEngine.validate_records("supplier_materials", records, SupplierMaterial)
        return [SupplierMaterial(**r) for r in valid]

    def load_inventory_policies(self) -> list[InventoryPolicy]:
        records = self._read_records("inventory_policies", "inventory_policies.csv")
        valid, report = ValidationEngine.validate_records("inventory_policies", records, InventoryPolicy)
        return [InventoryPolicy(**r) for r in valid]

    def load_inventory(self) -> list[InventorySnapshot]:
        records = self._read_records("inventory", "inventory.csv")
        valid, report = ValidationEngine.validate_records("inventory", records, InventorySnapshot)
        return [InventorySnapshot(**r) for r in valid]

    def load_production_orders(self) -> list[ProductionOrder]:
        records = self._read_records("production_orders", "production_orders.csv")
        valid, report = ValidationEngine.validate_records("production_orders", records, ProductionOrder)
        return [ProductionOrder(**r) for r in valid]

    def load_purchase_orders(self) -> list[PurchaseOrder]:
        records = self._read_records("purchase_orders", "purchase_orders.csv")
        valid, report = ValidationEngine.validate_records("purchase_orders", records, PurchaseOrder)
        return [PurchaseOrder(**r) for r in valid]

    def load_demand_forecast(self) -> list[DemandForecastLine]:
        records = self._read_records("demand_forecast", "demand_forecast.csv")
        valid, report = ValidationEngine.validate_records("demand_forecast", records, DemandForecastLine)
        return [DemandForecastLine(**r) for r in valid]

    def load_inventory_transactions(self) -> list[InventoryTransaction]:
        records = self._read_records("inventory_transactions", "inventory_transactions.csv")
        valid, report = ValidationEngine.validate_records("inventory_transactions", records, InventoryTransaction)
        return [InventoryTransaction(**r) for r in valid]

    def load_managers(self) -> list[Manager]:
        records = self._read_records("managers", "managers.csv")
        valid, report = ValidationEngine.validate_records("managers", records, Manager)
        return [Manager(**r) for r in valid]


@lru_cache(maxsize=1)
def _cached_connector(data_dir: str) -> CsvConnector:
    return CsvConnector(data_dir)


def get_connector(data_dir: str | None = None) -> BaseConnector:
    """Factory helper preserving original function signature."""
    from config.settings import settings
    from connectors.connector_factory import ConnectorFactory
    return ConnectorFactory.create(data_source="csv", data_dir=data_dir or settings.csv_data_dir)

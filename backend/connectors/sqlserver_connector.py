"""
SQL Server / SSMS / Azure SQL Connector.

Queries relational database tables or views and transforms enterprise records into canonical models.
Supports fallback to local CSV data when live database connections are unconfigured in local dev.
"""
from __future__ import annotations

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
    PurchaseOrder, DemandForecastLine, InventoryTransaction, Manager
)

logger = logging.getLogger(__name__)


@register_connector("sqlserver", "ssms", "azuresql")
class SqlServerConnector(BaseConnector):
    """Microsoft SQL Server relational database connector."""

    def __init__(
        self,
        connection_string: str | None = None,
        data_dir: str | Path | None = None,
        mapping_file: str | Path | None = None
    ):
        self.connection_string = connection_string
        self.data_dir = Path(data_dir) if data_dir else None
        mapping_path = mapping_file or (get_default_mapping_dir() / "sqlserver.json")
        self.mapping_engine = MappingEngine.load_from_file(mapping_path)

    def _query_table_or_fallback(self, entity_name: str, table_name: str, fallback_csv: str) -> list[dict]:
        if self.connection_string:
            try:
                # Execute SQL query via SQLAlchemy if connection string is provided
                import sqlalchemy
                engine = sqlalchemy.create_engine(self.connection_string)
                with engine.connect() as conn:
                    df = pd.read_sql_table(table_name, conn)
                    df = df.where(pd.notnull(df), None)
                    raw_records = df.to_dict("records")
                    return self.mapping_engine.map_records(entity_name, raw_records)
            except Exception as e:
                logger.warning(f"Failed to query SQL Server table '{table_name}': {e}. Falling back to CSV.")

        # Fallback to CSV files if database connection is unavailable
        if self.data_dir:
            csv_path = self.data_dir / fallback_csv
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                df = df.where(pd.notnull(df), None)
                raw_records = df.to_dict("records")
                return self.mapping_engine.map_records(entity_name, raw_records)

        return []

    def load_plants(self) -> list[Plant]:
        recs = self._query_table_or_fallback("plants", "dim_plant", "plants.csv")
        valid, _ = ValidationEngine.validate_records("plants", recs, Plant)
        return [Plant(**r) for r in valid]

    def load_warehouses(self) -> list[Warehouse]:
        recs = self._query_table_or_fallback("warehouses", "dim_warehouse", "warehouses.csv")
        valid, _ = ValidationEngine.validate_records("warehouses", recs, Warehouse)
        return [Warehouse(**r) for r in valid]

    def load_product_families(self) -> list[ProductFamily]:
        recs = self._query_table_or_fallback("product_families", "dim_product_family", "product_families.csv")
        valid, _ = ValidationEngine.validate_records("product_families", recs, ProductFamily)
        return [ProductFamily(**r) for r in valid]

    def load_products(self) -> list[Product]:
        recs = self._query_table_or_fallback("products", "dim_product", "products.csv")
        valid, _ = ValidationEngine.validate_records("products", recs, Product)
        return [Product(**r) for r in valid]

    def load_materials(self) -> list[Material]:
        recs = self._query_table_or_fallback("materials", "dim_material", "materials.csv")
        valid, _ = ValidationEngine.validate_records("materials", recs, Material)
        return [Material(**r) for r in valid]

    def load_bom(self) -> list[BomLine]:
        recs = self._query_table_or_fallback("bom", "fact_bom", "bom.csv")
        valid, _ = ValidationEngine.validate_records("bom", recs, BomLine)
        return [BomLine(**r) for r in valid]

    def load_suppliers(self) -> list[Supplier]:
        recs = self._query_table_or_fallback("suppliers", "dim_supplier", "suppliers.csv")
        for r in recs:
            if "preferred_supplier" in r and isinstance(r["preferred_supplier"], str):
                r["preferred_supplier"] = r["preferred_supplier"].upper() == "Y"
        valid, _ = ValidationEngine.validate_records("suppliers", recs, Supplier)
        return [Supplier(**r) for r in valid]

    def load_supplier_materials(self) -> list[SupplierMaterial]:
        recs = self._query_table_or_fallback("supplier_materials", "fact_supplier_material", "supplier_materials.csv")
        for r in recs:
            if "is_primary_supplier" in r and isinstance(r["is_primary_supplier"], str):
                r["is_primary_supplier"] = r["is_primary_supplier"].upper() == "Y"
        valid, _ = ValidationEngine.validate_records("supplier_materials", recs, SupplierMaterial)
        return [SupplierMaterial(**r) for r in valid]

    def load_inventory_policies(self) -> list[InventoryPolicy]:
        recs = self._query_table_or_fallback("inventory_policies", "fact_inventory_policy", "inventory_policies.csv")
        valid, _ = ValidationEngine.validate_records("inventory_policies", recs, InventoryPolicy)
        return [InventoryPolicy(**r) for r in valid]

    def load_inventory(self) -> list[InventorySnapshot]:
        recs = self._query_table_or_fallback("inventory", "fact_inventory_snapshot", "inventory.csv")
        valid, _ = ValidationEngine.validate_records("inventory", recs, InventorySnapshot)
        return [InventorySnapshot(**r) for r in valid]

    def load_production_orders(self) -> list[ProductionOrder]:
        recs = self._query_table_or_fallback("production_orders", "fact_production_order", "production_orders.csv")
        valid, _ = ValidationEngine.validate_records("production_orders", recs, ProductionOrder)
        return [ProductionOrder(**r) for r in valid]

    def load_purchase_orders(self) -> list[PurchaseOrder]:
        recs = self._query_table_or_fallback("purchase_orders", "fact_purchase_order", "purchase_orders.csv")
        valid, _ = ValidationEngine.validate_records("purchase_orders", recs, PurchaseOrder)
        return [PurchaseOrder(**r) for r in valid]

    def load_demand_forecast(self) -> list[DemandForecastLine]:
        recs = self._query_table_or_fallback("demand_forecast", "fact_demand_forecast", "demand_forecast.csv")
        valid, _ = ValidationEngine.validate_records("demand_forecast", recs, DemandForecastLine)
        return [DemandForecastLine(**r) for r in valid]

    def load_inventory_transactions(self) -> list[InventoryTransaction]:
        recs = self._query_table_or_fallback("inventory_transactions", "fact_inventory_transaction", "inventory_transactions.csv")
        valid, _ = ValidationEngine.validate_records("inventory_transactions", recs, InventoryTransaction)
        return [InventoryTransaction(**r) for r in valid]

    def load_managers(self) -> list[Manager]:
        recs = self._query_table_or_fallback("managers", "dim_manager", "managers.csv")
        valid, _ = ValidationEngine.validate_records("managers", recs, Manager)
        return [Manager(**r) for r in valid]

"""
Excel Connector — Reads enterprise data from multi-sheet Excel workbooks (.xlsx, .xls).
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


@register_connector("excel", "excel_connector")
class ExcelConnector(BaseConnector):
    """Connector for reading supply chain data from Excel spreadsheets."""

    def __init__(self, excel_file: str | Path | None = None, data_dir: str | Path | None = None, mapping_file: str | Path | None = None):
        self.excel_file = Path(excel_file) if excel_file else None
        self.data_dir = Path(data_dir) if data_dir else None
        mapping_path = mapping_file or (get_default_mapping_dir() / "csv.json")
        self.mapping_engine = MappingEngine.load_from_file(mapping_path)

    def _read_sheet_or_csv(self, sheet_name: str, fallback_csv: str) -> list[dict]:
        if self.excel_file and self.excel_file.exists():
            try:
                df = pd.read_excel(self.excel_file, sheet_name=sheet_name)
                df = df.where(pd.notnull(df), None)
                raw_records = df.to_dict("records")
                return self.mapping_engine.map_records(sheet_name.lower(), raw_records)
            except Exception as e:
                logger.warning(f"Could not read sheet '{sheet_name}' from Excel file {self.excel_file}: {e}")
        
        # Fallback to CSV directory if Excel file or sheet is unavailable
        if self.data_dir:
            csv_path = self.data_dir / fallback_csv
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                df = df.where(pd.notnull(df), None)
                raw_records = df.to_dict("records")
                return self.mapping_engine.map_records(sheet_name.lower(), raw_records)
        
        return []

    def load_plants(self) -> list[Plant]:
        recs = self._read_sheet_or_csv("Plants", "plants.csv")
        valid, _ = ValidationEngine.validate_records("plants", recs, Plant)
        return [Plant(**r) for r in valid]

    def load_warehouses(self) -> list[Warehouse]:
        recs = self._read_sheet_or_csv("Warehouses", "warehouses.csv")
        valid, _ = ValidationEngine.validate_records("warehouses", recs, Warehouse)
        return [Warehouse(**r) for r in valid]

    def load_product_families(self) -> list[ProductFamily]:
        recs = self._read_sheet_or_csv("ProductFamilies", "product_families.csv")
        valid, _ = ValidationEngine.validate_records("product_families", recs, ProductFamily)
        return [ProductFamily(**r) for r in valid]

    def load_products(self) -> list[Product]:
        recs = self._read_sheet_or_csv("Products", "products.csv")
        valid, _ = ValidationEngine.validate_records("products", recs, Product)
        return [Product(**r) for r in valid]

    def load_materials(self) -> list[Material]:
        recs = self._read_sheet_or_csv("Materials", "materials.csv")
        valid, _ = ValidationEngine.validate_records("materials", recs, Material)
        return [Material(**r) for r in valid]

    def load_bom(self) -> list[BomLine]:
        recs = self._read_sheet_or_csv("BOM", "bom.csv")
        valid, _ = ValidationEngine.validate_records("bom", recs, BomLine)
        return [BomLine(**r) for r in valid]

    def load_suppliers(self) -> list[Supplier]:
        recs = self._read_sheet_or_csv("Suppliers", "suppliers.csv")
        for r in recs:
            if "preferred_supplier" in r and isinstance(r["preferred_supplier"], str):
                r["preferred_supplier"] = r["preferred_supplier"].upper() == "Y"
        valid, _ = ValidationEngine.validate_records("suppliers", recs, Supplier)
        return [Supplier(**r) for r in valid]

    def load_supplier_materials(self) -> list[SupplierMaterial]:
        recs = self._read_sheet_or_csv("SupplierMaterials", "supplier_materials.csv")
        for r in recs:
            if "is_primary_supplier" in r and isinstance(r["is_primary_supplier"], str):
                r["is_primary_supplier"] = r["is_primary_supplier"].upper() == "Y"
        valid, _ = ValidationEngine.validate_records("supplier_materials", recs, SupplierMaterial)
        return [SupplierMaterial(**r) for r in valid]

    def load_inventory_policies(self) -> list[InventoryPolicy]:
        recs = self._read_sheet_or_csv("InventoryPolicies", "inventory_policies.csv")
        valid, _ = ValidationEngine.validate_records("inventory_policies", recs, InventoryPolicy)
        return [InventoryPolicy(**r) for r in valid]

    def load_inventory(self) -> list[InventorySnapshot]:
        recs = self._read_sheet_or_csv("Inventory", "inventory.csv")
        valid, _ = ValidationEngine.validate_records("inventory", recs, InventorySnapshot)
        return [InventorySnapshot(**r) for r in valid]

    def load_production_orders(self) -> list[ProductionOrder]:
        recs = self._read_sheet_or_csv("ProductionOrders", "production_orders.csv")
        valid, _ = ValidationEngine.validate_records("production_orders", recs, ProductionOrder)
        return [ProductionOrder(**r) for r in valid]

    def load_purchase_orders(self) -> list[PurchaseOrder]:
        recs = self._read_sheet_or_csv("PurchaseOrders", "purchase_orders.csv")
        valid, _ = ValidationEngine.validate_records("purchase_orders", recs, PurchaseOrder)
        return [PurchaseOrder(**r) for r in valid]

    def load_demand_forecast(self) -> list[DemandForecastLine]:
        recs = self._read_sheet_or_csv("DemandForecast", "demand_forecast.csv")
        valid, _ = ValidationEngine.validate_records("demand_forecast", recs, DemandForecastLine)
        return [DemandForecastLine(**r) for r in valid]

    def load_inventory_transactions(self) -> list[InventoryTransaction]:
        recs = self._read_sheet_or_csv("InventoryTransactions", "inventory_transactions.csv")
        valid, _ = ValidationEngine.validate_records("inventory_transactions", recs, InventoryTransaction)
        return [InventoryTransaction(**r) for r in valid]

    def load_managers(self) -> list[Manager]:
        recs = self._read_sheet_or_csv("Managers", "managers.csv")
        valid, _ = ValidationEngine.validate_records("managers", recs, Manager)
        return [Manager(**r) for r in valid]

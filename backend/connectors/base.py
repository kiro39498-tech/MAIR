"""
Base Connector Abstraction (SSOT Section 6, Pluggable Architecture).

All enterprise data connectors (CSV, Excel, SQL Server, PostgreSQL, MySQL, Oracle,
SAP, Fabric, REST, S3/Azure Blob, SharePoint) must inherit from BaseConnector.

Every connector converts enterprise source schemas into unified canonical models.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from models.canonical import (
    Plant, Warehouse, ProductFamily, Product, Material, BomLine, Supplier,
    SupplierMaterial, InventoryPolicy, InventorySnapshot, ProductionOrder,
    PurchaseOrder, DemandForecastLine, InventoryTransaction, Manager, Batch,
    Reservation
)


class BaseConnector(ABC):
    """Abstract Base Class for pluggable enterprise data connectors."""

    @abstractmethod
    def load_materials() -> list[Material]:
        """Load and return all materials in canonical format."""
        ...

    @abstractmethod
    def load_inventory() -> list[InventorySnapshot]:
        """Load and return inventory snapshot records in canonical format."""
        ...

    @abstractmethod
    def load_bom() -> list[BomLine]:
        """Load and return Bills of Materials (BOM) components."""
        ...

    @abstractmethod
    def load_purchase_orders() -> list[PurchaseOrder]:
        """Load open and historical purchase orders."""
        ...

    @abstractmethod
    def load_suppliers() -> list[Supplier]:
        """Load master supplier directory."""
        ...

    @abstractmethod
    def load_inventory_policies() -> list[InventoryPolicy]:
        """Load safety stock, reorder point, and max stock policies."""
        ...

    @abstractmethod
    def load_production_orders() -> list[ProductionOrder]:
        """Load scheduled and active production orders."""
        ...

    @abstractmethod
    def load_plants() -> list[Plant]:
        """Load manufacturing plants."""
        ...

    @abstractmethod
    def load_warehouses() -> list[Warehouse]:
        """Load storage locations and warehouses."""
        ...

    @abstractmethod
    def load_products() -> list[Product]:
        """Load finished products."""
        ...

    @abstractmethod
    def load_product_families() -> list[ProductFamily]:
        """Load product families."""
        ...

    @abstractmethod
    def load_supplier_materials() -> list[SupplierMaterial]:
        """Load supplier-material contracts and lead times."""
        ...

    @abstractmethod
    def load_demand_forecast() -> list[DemandForecastLine]:
        """Load consensus demand forecasts."""
        ...

    @abstractmethod
    def load_inventory_transactions() -> list[InventoryTransaction]:
        """Load inventory goods movements."""
        ...

    @abstractmethod
    def load_managers() -> list[Manager]:
        """Load plant managers for approval routing."""
        ...

    def load_batches(self) -> list[Batch]:
        """Optional: Load material batches/lots. Default empty implementation."""
        return []

    def load_reservations(self) -> list[Reservation]:
        """Optional: Load hard component reservations. Default empty implementation."""
        return []

    # --- Backward compatibility aliases (get_* methods) ---
    def get_plants(self) -> list[Plant]:
        return self.load_plants()

    def get_warehouses(self) -> list[Warehouse]:
        return self.load_warehouses()

    def get_product_families(self) -> list[ProductFamily]:
        return self.load_product_families()

    def get_products(self) -> list[Product]:
        return self.load_products()

    def get_materials(self) -> list[Material]:
        return self.load_materials()

    def get_bom(self) -> list[BomLine]:
        return self.load_bom()

    def get_suppliers(self) -> list[Supplier]:
        return self.load_suppliers()

    def get_supplier_materials(self) -> list[SupplierMaterial]:
        return self.load_supplier_materials()

    def get_inventory_policies(self) -> list[InventoryPolicy]:
        return self.load_inventory_policies()

    def get_inventory(self) -> list[InventorySnapshot]:
        return self.load_inventory()

    def get_production_orders(self) -> list[ProductionOrder]:
        return self.load_production_orders()

    def get_purchase_orders(self) -> list[PurchaseOrder]:
        return self.load_purchase_orders()

    def get_demand_forecast(self) -> list[DemandForecastLine]:
        return self.load_demand_forecast()

    def get_inventory_transactions(self) -> list[InventoryTransaction]:
        return self.load_inventory_transactions()

    def get_managers(self) -> list[Manager]:
        return self.load_managers()

    def get_batches(self) -> list[Batch]:
        return self.load_batches()

    def get_reservations(self) -> list[Reservation]:
        return self.load_reservations()

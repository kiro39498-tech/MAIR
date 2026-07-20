"""
Connector contract (SSOT section 6, plug-and-play architecture). Any new
enterprise data source (SAP, SQL Server, Fabric, REST) implements this
interface and maps its native schema into the canonical models. Nothing
above this layer — analytics, MCP, agents — needs to know or care which
connector is in use.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from models.schemas import (
    Plant, Warehouse, ProductFamily, Product, Material, BomLine, Supplier,
    SupplierMaterial, InventoryPolicy, InventorySnapshot, ProductionOrder,
    PurchaseOrder, DemandForecastLine, InventoryTransaction, Manager,
)


class BaseConnector(ABC):
    @abstractmethod
    def get_plants(self) -> list[Plant]: ...

    @abstractmethod
    def get_warehouses(self) -> list[Warehouse]: ...

    @abstractmethod
    def get_product_families(self) -> list[ProductFamily]: ...

    @abstractmethod
    def get_products(self) -> list[Product]: ...

    @abstractmethod
    def get_materials(self) -> list[Material]: ...

    @abstractmethod
    def get_bom(self) -> list[BomLine]: ...

    @abstractmethod
    def get_suppliers(self) -> list[Supplier]: ...

    @abstractmethod
    def get_supplier_materials(self) -> list[SupplierMaterial]: ...

    @abstractmethod
    def get_inventory_policies(self) -> list[InventoryPolicy]: ...

    @abstractmethod
    def get_inventory(self) -> list[InventorySnapshot]: ...

    @abstractmethod
    def get_production_orders(self) -> list[ProductionOrder]: ...

    @abstractmethod
    def get_purchase_orders(self) -> list[PurchaseOrder]: ...

    @abstractmethod
    def get_demand_forecast(self) -> list[DemandForecastLine]: ...

    @abstractmethod
    def get_inventory_transactions(self) -> list[InventoryTransaction]: ...

    @abstractmethod
    def get_managers(self) -> list[Manager]: ...

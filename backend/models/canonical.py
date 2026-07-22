"""
Canonical Manufacturing Data Models (SSOT Section 7).

Every data connector maps source enterprise data (SAP, SQL Server, Fabric,
Excel, CSV, REST) into these unified, enterprise-grade Pydantic models.

Analytics engines, MCP tools, and multi-agent systems operate exclusively on
these canonical objects — never native source schemas.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class Plant(BaseModel):
    plant_id: str = Field(..., description="Unique plant identifier (e.g. P001, WERKS 1000)")
    plant_name: str = Field(..., description="Plant display name")
    country: str = Field(default="US", description="Plant country code")
    region: str = Field(default="NA", description="Operating region")
    plant_type: str = Field(default="Manufacturing", description="Plant facility type")
    timezone: str = Field(default="UTC", description="Plant local timezone")


class Warehouse(BaseModel):
    warehouse_id: str = Field(..., description="Unique warehouse/storage location ID (LGORT)")
    warehouse_name: str = Field(..., description="Warehouse display name")
    plant_id: str = Field(..., description="Associated plant ID")
    warehouse_type: str = Field(default="Standard", description="Warehouse classification")
    capacity_units: int = Field(default=10000, description="Max storage capacity units")


class ProductFamily(BaseModel):
    family_id: str = Field(..., description="Unique product family ID")
    family_name: str = Field(..., description="Product family name")
    description: str = Field(default="", description="Family description")


class Product(BaseModel):
    product_id: str = Field(..., description="Unique finished product ID (FG/MATNR)")
    product_name: str = Field(..., description="Product description")
    family_id: str = Field(..., description="Product family ID")
    primary_plant_id: str = Field(..., description="Primary manufacturing plant ID")
    unit_of_measure: str = Field(default="EA", description="Base unit of measure (MEINS)")
    standard_cost: float = Field(default=0.0, description="Standard cost per unit")
    lifecycle_status: str = Field(default="Active", description="Product lifecycle status")


class Material(BaseModel):
    material_id: str = Field(..., description="Unique material/component ID (MATNR)")
    material_name: str = Field(..., description="Material description (MAKTX)")
    material_type: str = Field(default="RAW", description="Material type (ROH, HALB, FERT)")
    unit_of_measure: str = Field(default="EA", description="Base unit of measure")
    standard_cost: float = Field(default=0.0, description="Standard unit cost")
    criticality: str = Field(default="Medium", description="High / Medium / Low operational criticality")
    abc_class: str = Field(default="B", description="ABC classification (A, B, C)")


class BomLine(BaseModel):
    bom_id: str = Field(..., description="BOM header ID")
    product_id: str = Field(..., description="Parent product ID")
    material_id: str = Field(..., description="Child component material ID")
    quantity_per_unit: float = Field(..., description="Component quantity required per parent unit")
    bom_version: str = Field(default="1.0", description="BOM version")
    effective_date: date = Field(default_factory=date.today, description="BOM line effective start date")


class Supplier(BaseModel):
    supplier_id: str = Field(..., description="Unique supplier ID (LIFNR)")
    supplier_name: str = Field(..., description="Supplier company name")
    country: str = Field(default="US", description="Supplier country")
    reliability_score: int = Field(default=90, description="Historical reliability score (0-100)")
    preferred_supplier: bool = Field(default=False, description="Preferred supplier flag")
    payment_terms: str = Field(default="Net 30", description="Payment terms")


class SupplierMaterial(BaseModel):
    supplier_material_id: str = Field(..., description="Supplier-Material relationship key")
    supplier_id: str = Field(..., description="Supplier ID")
    material_id: str = Field(..., description="Material ID")
    unit_price: float = Field(..., description="Contracted unit price")
    lead_time_days: int = Field(..., description="Supplier replenishment lead time in days")
    moq: int = Field(default=1, description="Minimum Order Quantity (MOQ)")
    is_primary_supplier: bool = Field(default=True, description="Primary supplier flag")


class InventoryPolicy(BaseModel):
    material_id: str = Field(..., description="Material ID")
    plant_id: str = Field(..., description="Plant ID")
    avg_daily_usage: float = Field(..., description="Average daily consumption rate")
    safety_stock_qty: float = Field(..., description="Safety stock threshold (SS)")
    reorder_point_qty: float = Field(..., description="Reorder point threshold (ROP)")
    max_stock_qty: float = Field(..., description="Maximum stock capacity (MS)")
    reorder_qty: float = Field(..., description="Target reorder quantity (EOQ)")


class InventorySnapshot(BaseModel):
    material_id: str = Field(..., description="Material ID")
    plant_id: str = Field(..., description="Plant ID")
    warehouse_id: str = Field(default="WH01", description="Warehouse ID")
    unrestricted_qty: float = Field(default=0.0, description="Unrestricted on-hand inventory (LABST)")
    quality_hold_qty: float = Field(default=0.0, description="Quality inspection stock (INSME)")
    blocked_qty: float = Field(default=0.0, description="Blocked stock (SPEME)")
    reserved_qty: float = Field(default=0.0, description="Hard-reserved stock for production")
    snapshot_date: date = Field(default_factory=date.today, description="Inventory snapshot date")

    @property
    def usable_qty(self) -> float:
        """Usable inventory available for production (Unrestricted - Reserved)."""
        return max(0.0, self.unrestricted_qty - self.reserved_qty)


class Batch(BaseModel):
    batch_id: str = Field(..., description="Unique batch/lot number (CHARG)")
    material_id: str = Field(..., description="Material ID")
    plant_id: str = Field(..., description="Plant ID")
    quantity: float = Field(..., description="Batch quantity")
    manufacturing_date: date = Field(..., description="Batch production date")
    expiry_date: Optional[date] = Field(None, description="Expiration date")
    status: str = Field(default="Unrestricted", description="Batch status (Unrestricted, Restricted, Blocked)")


class Reservation(BaseModel):
    reservation_id: str = Field(..., description="Production reservation ID (RSNUM)")
    production_order_id: str = Field(..., description="Associated production order ID")
    material_id: str = Field(..., description="Reserved material ID")
    plant_id: str = Field(..., description="Plant ID")
    reserved_qty: float = Field(..., description="Reserved quantity")
    requirement_date: date = Field(..., description="Date material is required on line")


class ProductionOrder(BaseModel):
    production_order_id: str = Field(..., description="Production order number (AUFNR)")
    product_id: str = Field(..., description="Product being manufactured")
    plant_id: str = Field(..., description="Plant ID")
    order_qty: int = Field(..., description="Target production order quantity")
    start_date: date = Field(..., description="Scheduled production start date")
    due_date: date = Field(..., description="Scheduled production completion date")
    status: str = Field(default="Released", description="Order status (Released, In Process, Confirmed, Delayed)")
    priority: str = Field(default="Medium", description="Order priority (High, Medium, Low)")


class PurchaseOrder(BaseModel):
    po_id: str = Field(..., description="Purchase order number (EBELN)")
    po_line: int = Field(default=10, description="Purchase order line item (EBELP)")
    material_id: str = Field(..., description="Material ID")
    supplier_id: str = Field(..., description="Supplier ID")
    plant_id: str = Field(..., description="Plant ID")
    order_qty: int = Field(..., description="Ordered quantity")
    open_qty: int = Field(..., description="Remaining unfulfilled quantity")
    unit_price: float = Field(..., description="Unit purchase price")
    order_date: date = Field(..., description="PO creation date")
    expected_receipt_date: date = Field(..., description="Expected delivery date")
    status: str = Field(default="Open", description="PO line status (Open, Partially Received, Late, Closed)")


class DemandForecastLine(BaseModel):
    forecast_id: str = Field(..., description="Forecast line ID")
    product_id: str = Field(..., description="Product ID")
    plant_id: str = Field(..., description="Plant ID")
    forecast_week_start: date = Field(..., description="Forecast week start date")
    forecast_qty: int = Field(..., description="Projected demand quantity")
    forecast_type: str = Field(default="Consensus", description="Forecast methodology/type")


class InventoryTransaction(BaseModel):
    transaction_id: str = Field(..., description="Transaction document number (MBLNR)")
    material_id: str = Field(..., description="Material ID")
    plant_id: str = Field(..., description="Plant ID")
    warehouse_id: str = Field(..., description="Warehouse ID")
    transaction_type: str = Field(..., description="Movement type (101-Receipt, 261-Issue, 311-Transfer)")
    quantity: int = Field(..., description="Transacted quantity")
    transaction_date: date = Field(..., description="Posting date")
    reference_doc: str = Field(default="", description="Reference document ID")


class Manager(BaseModel):
    manager_id: str = Field(..., description="Manager employee ID")
    manager_name: str = Field(..., description="Manager name")
    plant_id: str = Field(..., description="Managed plant ID")
    role: str = Field(default="Plant Manager", description="Role title")
    notification_channel: str = Field(default="Email", description="Preferred channel")
    approval_threshold_value: int = Field(default=50000, description="Max PO approval limit")

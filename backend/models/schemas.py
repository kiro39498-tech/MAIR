"""
Canonical manufacturing data model (SSOT section 7). Every connector must
map its source data into these models. Analytics, MCP tools, and agents only
ever see this shape — never the source system's native schema.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class CreateActionRequest(BaseModel):
    material_id: str
    plant_id: str
    suggested_qty_override: Optional[int] = None
    suggested_supplier_override: Optional[str] = None


class Plant(BaseModel):
    plant_id: str
    plant_name: str
    country: str
    region: str
    plant_type: str
    timezone: str


class Warehouse(BaseModel):
    warehouse_id: str
    warehouse_name: str
    plant_id: str
    warehouse_type: str
    capacity_units: int


class ProductFamily(BaseModel):
    family_id: str
    family_name: str
    description: str


class Product(BaseModel):
    product_id: str
    product_name: str
    family_id: str
    primary_plant_id: str
    unit_of_measure: str
    standard_cost: float
    lifecycle_status: str


class Material(BaseModel):
    material_id: str
    material_name: str
    material_type: str
    unit_of_measure: str
    standard_cost: float
    criticality: str  # High / Medium / Low
    abc_class: str  # A / B / C


class BomLine(BaseModel):
    bom_id: str
    product_id: str
    material_id: str
    quantity_per_unit: float
    bom_version: str
    effective_date: date


class Supplier(BaseModel):
    supplier_id: str
    supplier_name: str
    country: str
    reliability_score: int
    preferred_supplier: bool
    payment_terms: str


class SupplierMaterial(BaseModel):
    supplier_material_id: str
    supplier_id: str
    material_id: str
    unit_price: float
    lead_time_days: int
    moq: int
    is_primary_supplier: bool


class InventoryPolicy(BaseModel):
    material_id: str
    plant_id: str
    avg_daily_usage: float
    safety_stock_qty: float
    reorder_point_qty: float
    max_stock_qty: float
    reorder_qty: float


class InventorySnapshot(BaseModel):
    material_id: str
    plant_id: str
    warehouse_id: str
    unrestricted_qty: float
    quality_hold_qty: float
    blocked_qty: float
    reserved_qty: float
    snapshot_date: date

    @property
    def usable_qty(self) -> float:
        """The only inventory number the analytics engine treats as usable.
        Quality-hold and blocked stock are on-hand but never usable."""
        return self.unrestricted_qty - self.reserved_qty


class ProductionOrder(BaseModel):
    production_order_id: str
    product_id: str
    plant_id: str
    order_qty: int
    start_date: date
    due_date: date
    status: str  # Released / In Process / Confirmed / Delayed
    priority: str  # High / Medium / Low


class PurchaseOrder(BaseModel):
    po_id: str
    po_line: int
    material_id: str
    supplier_id: str
    plant_id: str
    order_qty: int
    open_qty: int
    unit_price: float
    order_date: date
    expected_receipt_date: date
    status: str  # Open / Partially Received / Late / Closed


class DemandForecastLine(BaseModel):
    forecast_id: str
    product_id: str
    plant_id: str
    forecast_week_start: date
    forecast_qty: int
    forecast_type: str


class InventoryTransaction(BaseModel):
    transaction_id: str
    material_id: str
    plant_id: str
    warehouse_id: str
    transaction_type: str
    quantity: int
    transaction_date: date
    reference_doc: str


class Manager(BaseModel):
    manager_id: str
    manager_name: str
    plant_id: str
    role: str
    notification_channel: str
    approval_threshold_value: int


# --- Analytics output models (what the engine hands to MCP tools/agents) --

class MaterialHealth(BaseModel):
    material_id: str
    plant_id: str
    usable_qty: float
    safety_stock_qty: float
    reorder_point_qty: float
    max_stock_qty: float
    status: str  # Healthy / Near Reorder / Safety Stock Warning / Shortage / Excess
    reason: str


class ProjectionPoint(BaseModel):
    date: date
    projected_balance: float
    demand_qty: float
    supply_qty: float


class MaterialProjection(BaseModel):
    material_id: str
    plant_id: str
    starting_balance: float
    points: list[ProjectionPoint]
    shortage_date: Optional[date] = None
    shortage_qty: Optional[float] = None


class ProductionImpact(BaseModel):
    material_id: str
    plant_id: str
    affected_production_orders: list[str]
    total_qty_at_risk: int
    earliest_due_date: Optional[date] = None
    impact_severity: str  # High / Medium / Low


class PoCoverage(BaseModel):
    material_id: str
    plant_id: str
    open_po_qty: int
    earliest_expected_receipt: Optional[date] = None
    has_late_po: bool
    covers_shortfall: bool


class ReplenishmentRecommendation(BaseModel):
    material_id: str
    plant_id: str
    recommended_action: str  # Replenish / Expedite / Restore Safety Stock / Transfer / Monitor
    recommended_qty: Optional[int] = None
    suggested_supplier_id: Optional[str] = None
    lead_time_days: Optional[int] = None
    priority_score: float
    rationale: str


class ReplenishmentAction(BaseModel):
    action_id: str
    material_id: str
    plant_id: str
    recommended_action: str
    recommended_qty: Optional[int] = None
    suggested_supplier_id: Optional[str] = None
    priority_score: float
    rationale: str
    status: str
    approval_token: str
    notified_at: Optional[datetime] = None
    email_send_status: Optional[str] = None
    decided_at: Optional[datetime] = None
    decision_note: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ProductRiskRow(BaseModel):
    material_id: str
    material_name: str
    plant_id: str
    on_hand_qty: float
    safety_stock: float
    reorder_point: float
    max_stock: float
    health_status: str
    days_of_supply: float
    priority_score: float


class BlockingComponent(BaseModel):
    material_id: str
    health_status: str
    usable_qty: float
    reorder_point: float
    safety_stock: float
    shortfall: float


class ProductBomRiskRow(BaseModel):
    product_id: str
    product_name: str
    plant_id: str
    risk_status: str
    blocking_components: list[BlockingComponent]
    priority_score: float



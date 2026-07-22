"""
Canonical manufacturing data model (SSOT section 7). Every connector must
map its source data into these models. Analytics, MCP tools, and agents only
ever see this shape — never the source system's native schema.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel

# Re-export all canonical models from models/canonical.py for unified access
from models.canonical import (
    Plant,
    Warehouse,
    ProductFamily,
    Product,
    Material,
    BomLine,
    Supplier,
    SupplierMaterial,
    InventoryPolicy,
    InventorySnapshot,
    Batch,
    Reservation,
    ProductionOrder,
    PurchaseOrder,
    DemandForecastLine,
    InventoryTransaction,
    Manager,
)


class CreateActionRequest(BaseModel):
    material_id: str
    plant_id: str
    suggested_qty_override: Optional[int] = None
    suggested_supplier_override: Optional[str] = None


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


class BomComponent(BaseModel):
    """Full BOM component entry — every material in the product's BOM,
    regardless of health status. Non-blocking entries have shortfall=0."""
    material_id: str
    material_name: str
    health_status: str
    usable_qty: float
    reorder_point: float
    safety_stock: float
    qty_per_unit: float
    net_shortfall: float  # 0 for Healthy/Excess, positive only for blockers
    is_blocking: bool
    has_inventory_data: bool  # False when component has no policy at this plant


class ProductBomRiskRow(BaseModel):
    product_id: str
    product_name: str
    plant_id: str
    risk_status: str
    blocking_components: list[BlockingComponent]
    all_components: list[BomComponent]  # full BOM with all statuses
    priority_score: float


class MaterialUsageRow(BaseModel):
    product_id: str
    product_name: str
    plant_id: str
    risk_status: str
    qty_per_unit: float
    is_blocking: bool

"""
MCP server — the ONLY interface agents are allowed to use to reach data or
analytics (SSOT section 11: "Agents only communicate with the MCP layer").
Every tool here wraps a deterministic analytics function; no tool performs
its own business logic and no tool ever writes/executes anything in Phase 1.

Run standalone for testing:  python -m mcp_server.server
Agents spawn this as a stdio subprocess via MCPStdioTool (see agents/).
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from data.repository import get_repository
from analytics.health_classification import get_material_health, get_all_material_health
from analytics.bom_explosion import products_using_material, materials_used_by_product
from analytics.projection import project_material_balance
from analytics.po_analysis import analyze_po_coverage
from analytics.production_impact import get_production_impact
from analytics.priority_scoring import rank_at_risk_materials
from analytics.replenishment import recommend_for_material, draft_recommendations

mcp = FastMCP("material-availability-agent")


@mcp.tool()
def get_inventory(material_id: str, plant_id: str) -> dict:
    """Get the current usable inventory and health status for one material at one plant."""
    repo = get_repository()
    health = get_material_health(repo, material_id, plant_id)
    if health is None:
        return {"error": f"No inventory policy found for {material_id} at {plant_id}"}
    return health.model_dump()


@mcp.tool()
def get_material_status_list(status: str | None = None, top_n: int = 20) -> list[dict]:
    """List materials by health status (Healthy / Near Reorder / Safety Stock
    Warning / Shortage / Excess). Omit status to get all, capped at top_n."""
    repo = get_repository()
    results = get_all_material_health(repo, status_filter=status)
    return [r.model_dump() for r in results[:top_n]]


@mcp.tool()
def get_material(material_id: str) -> dict:
    """Get master data for a material: name, type, criticality, ABC class, cost."""
    repo = get_repository()
    m = repo.material_by_id.get(material_id)
    return m.model_dump() if m else {"error": f"Material {material_id} not found"}


@mcp.tool()
def get_bom(product_id: str) -> list[str]:
    """List the material IDs consumed by a product (its bill of materials)."""
    repo = get_repository()
    return materials_used_by_product(repo, product_id)


@mcp.tool()
def get_products_using_material(material_id: str) -> list[str]:
    """List the product IDs that consume a given material — used to trace
    which finished products a material shortage threatens."""
    repo = get_repository()
    return products_using_material(repo, material_id)


@mcp.tool()
def get_inventory_projection(material_id: str, plant_id: str, horizon_days: int = 60) -> dict:
    """Project a material's usable balance forward day-by-day using open
    production-order demand and open PO supply. Returns the first shortage
    date/quantity if the balance is projected to go negative."""
    repo = get_repository()
    projection = project_material_balance(repo, material_id, plant_id, horizon_days)
    return {
        "material_id": projection.material_id,
        "plant_id": projection.plant_id,
        "starting_balance": projection.starting_balance,
        "shortage_date": str(projection.shortage_date) if projection.shortage_date else None,
        "shortage_qty": projection.shortage_qty,
        "num_points": len(projection.points),
    }


@mcp.tool()
def get_open_purchase_orders(material_id: str, plant_id: str) -> dict:
    """Check open PO coverage for a material: total open quantity, earliest
    expected receipt, and whether any open PO is late."""
    repo = get_repository()
    coverage = analyze_po_coverage(repo, material_id, plant_id)
    return coverage.model_dump()


@mcp.tool()
def get_production_impact(material_id: str, plant_id: str) -> dict:
    """Get the production orders threatened by a shortage of this material at
    this plant, with total quantity at risk and impact severity."""
    repo = get_repository()
    impact = _get_production_impact_impl(repo, material_id, plant_id)
    return impact.model_dump()


def _get_production_impact_impl(repo, material_id, plant_id):
    from analytics.production_impact import get_production_impact as _impl
    return _impl(repo, material_id, plant_id)


@mcp.tool()
def get_supplier(material_id: str) -> list[dict]:
    """Get the supplier options (price, lead time, MOQ, primary flag) for a material."""
    repo = get_repository()
    options = repo.supplier_materials_by_material.get(material_id, [])
    return [o.model_dump() for o in options]


@mcp.tool()
def get_priority_ranked_materials(top_n: int = 20) -> list[dict]:
    """Get the top-N at-risk materials across all plants, ranked by a
    combined urgency / criticality / production-impact score."""
    repo = get_repository()
    return rank_at_risk_materials(repo, top_n=top_n)


@mcp.tool()
def get_recommendation(material_id: str, plant_id: str) -> dict:
    """Get the drafted replenishment recommendation for one material at one
    plant. DRAFT ONLY — this does not place or modify any order."""
    repo = get_repository()
    rec = recommend_for_material(repo, material_id, plant_id)
    return rec.model_dump() if rec else {"error": "No recommendation available"}


@mcp.tool()
def get_recommendations(top_n: int = 20) -> list[dict]:
    """Get drafted replenishment recommendations for the top-N at-risk
    materials. DRAFT ONLY — nothing here is executed against any source system."""
    repo = get_repository()
    recs = draft_recommendations(repo, top_n=top_n)
    return [r.model_dump() for r in recs]


@mcp.tool()
def create_replenishment_action(material_id: str, plant_id: str) -> dict:
    """Submit a replenishment recommendation for manager approval for a single material.
    This creates an action in 'PendingApproval' status and notifies stakeholders.
    NOTE: There is intentionally no MCP tool exposed for execution, only for creating
    actions and checking status, to ensure humans remain in the execution loop."""
    from persistence.db import SessionLocal
    from services.replenishment_orchestration import process_single_material
    
    db = SessionLocal()
    try:
        action = process_single_material(db, material_id, plant_id)
        if action:
            return action.model_dump()
        return {"error": "Could not create action or it was recommended to Monitor"}
    finally:
        db.close()


@mcp.tool()
def get_replenishment_action_status(action_id: str) -> dict:
    """Get the current status (e.g. Drafted, PendingApproval, Approved, Rejected, Executed) of an action."""
    from persistence.db import SessionLocal
    from persistence import repository
    
    db = SessionLocal()
    try:
        action = repository.get_action(db, action_id)
        if action:
            return {"action_id": action.action_id, "status": action.status, "decision_note": action.decision_note}
        return {"error": f"Action {action_id} not found"}
    finally:
        db.close()


@mcp.tool()
def list_pending_replenishment_actions() -> list[dict]:
    """List all replenishment actions currently waiting for approval."""
    from persistence.db import SessionLocal
    from persistence import repository
    
    db = SessionLocal()
    try:
        actions = repository.list_actions(db, status="PendingApproval")
        return [a.model_dump() for a in actions]
    finally:
        db.close()


# NOTE: The execution tool (creating the actual PO) is deliberately omitted from MCP
# to ensure humans remain in the execution loop. It is only accessible via the REST API.

if __name__ == "__main__":
    mcp.run(transport="stdio")

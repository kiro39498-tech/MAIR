"""
Inventory health classification. Pure deterministic business rules — no AI
involved (SSOT core principle: "AI never performs inventory or
manufacturing calculations").

Boundaries are expressed relative to the material's own policy (safety
stock / reorder point / max stock), not to each other, because those three
values vary independently per material-plant. See tests/test_health_classification.py
for validation against the dataset's answer key.
"""
from __future__ import annotations

from config.settings import settings
from data.repository import Repository
from models.schemas import InventoryPolicy, MaterialHealth
from analytics.inventory_calc import get_usable_inventory


def classify(usable_qty: float, policy: InventoryPolicy) -> tuple[str, str]:
    ss, rp, ms = policy.safety_stock_qty, policy.reorder_point_qty, policy.max_stock_qty

    if usable_qty < ss * settings.shortage_ratio_of_safety_stock:
        return "Shortage", (
            f"Usable quantity ({usable_qty:.0f}) is critically below safety "
            f"stock ({ss:.0f}) — immediate risk of stockout."
        )
    if usable_qty < rp * settings.near_reorder_lower_ratio_of_rop:
        return "Safety Stock Warning", (
            f"Usable quantity ({usable_qty:.0f}) is below safety stock "
            f"({ss:.0f}) but not yet critical."
        )
    if usable_qty < rp * settings.near_reorder_upper_ratio_of_rop:
        return "Near Reorder", (
            f"Usable quantity ({usable_qty:.0f}) is approaching the reorder "
            f"point ({rp:.0f})."
        )
    if usable_qty > ms * settings.excess_ratio_of_max_stock:
        return "Excess", (
            f"Usable quantity ({usable_qty:.0f}) exceeds max stock "
            f"({ms:.0f}) — working capital opportunity."
        )
    return "Healthy", f"Usable quantity ({usable_qty:.0f}) is within normal range."


def get_material_health(repo: Repository, material_id: str, plant_id: str) -> MaterialHealth | None:
    policy = repo.policy_by_key.get((material_id, plant_id))
    if policy is None:
        return None
    
    # Calculate lead-time adjusted ROP
    from analytics.replenishment import _pick_supplier
    supplier = _pick_supplier(repo, material_id)
    lead_time = supplier.lead_time_days if supplier else 0
    adjusted_rop = policy.avg_daily_usage * lead_time + policy.safety_stock_qty
    
    policy_adjusted = policy.model_copy(update={"reorder_point_qty": adjusted_rop})
    
    usable = get_usable_inventory(repo, material_id, plant_id)
    status, reason = classify(usable, policy_adjusted)
    return MaterialHealth(
        material_id=material_id,
        plant_id=plant_id,
        usable_qty=usable,
        safety_stock_qty=policy_adjusted.safety_stock_qty,
        reorder_point_qty=policy_adjusted.reorder_point_qty,
        max_stock_qty=policy_adjusted.max_stock_qty,
        status=status,
        reason=reason,
    )



def get_all_material_health(repo: Repository, status_filter: str | None = None) -> list[MaterialHealth]:
    results = []
    for (material_id, plant_id) in repo.policy_by_key.keys():
        health = get_material_health(repo, material_id, plant_id)
        if health and (status_filter is None or health.status == status_filter):
            results.append(health)
    return results

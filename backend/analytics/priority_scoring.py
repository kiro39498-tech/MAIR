"""
Priority scoring — ranks at-risk materials so a planner (or the Replenishment
Agent) knows what to act on first. Combines urgency (how close to/below
safety stock), material criticality, and production impact into one score.
Weights are a tuning knob, not a hidden judgment call — keep them here,
in one place, so they can be revisited without touching other modules.
"""
from __future__ import annotations

from data.repository import Repository
from analytics.health_classification import get_material_health
from analytics.production_impact import get_production_impact

STATUS_URGENCY = {
    "Shortage": 1.0,
    "Safety Stock Warning": 0.7,
    "Near Reorder": 0.4,
    "Healthy": 0.05,
    "Excess": 0.1,
}
CRITICALITY_WEIGHT = {"High": 1.0, "Medium": 0.6, "Low": 0.3}
IMPACT_WEIGHT = {"High": 1.0, "Medium": 0.6, "Low": 0.2}

W_URGENCY, W_CRITICALITY, W_IMPACT = 0.45, 0.25, 0.30


def score_material(repo: Repository, material_id: str, plant_id: str) -> float:
    health = get_material_health(repo, material_id, plant_id)
    if health is None:
        return 0.0
    material = repo.material_by_id.get(material_id)
    impact = get_production_impact(repo, material_id, plant_id)

    urgency = STATUS_URGENCY.get(health.status, 0.0)
    criticality = CRITICALITY_WEIGHT.get(material.criticality, 0.3) if material else 0.3
    impact_score = IMPACT_WEIGHT.get(impact.impact_severity, 0.2)

    return round(W_URGENCY * urgency + W_CRITICALITY * criticality + W_IMPACT * impact_score, 4)


def rank_at_risk_materials(repo: Repository, top_n: int = 20) -> list[dict]:
    at_risk_statuses = {"Shortage", "Safety Stock Warning", "Near Reorder"}
    scored = []
    for (material_id, plant_id) in repo.policy_by_key.keys():
        health = get_material_health(repo, material_id, plant_id)
        if health and health.status in at_risk_statuses:
            scored.append({
                "material_id": material_id,
                "plant_id": plant_id,
                "status": health.status,
                "score": score_material(repo, material_id, plant_id),
            })
    scored.sort(key=lambda r: r["score"], reverse=True)
    return scored[:top_n]

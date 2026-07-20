import logging
from sqlalchemy.orm import Session

from data.repository import get_repository
from analytics import replenishment, health_classification
from services import replenishment_workflow, notification_service
from persistence import repository
from models.schemas import ReplenishmentAction

logger = logging.getLogger(__name__)

def process_single_recommendation(db: Session, repo, rec) -> ReplenishmentAction | None:
    if rec.recommended_action == "Monitor":
        return None
        
    try:
        # 1. Create action
        action, was_created = replenishment_workflow.create_action_from_recommendation(db, rec)
        if not was_created:
            return action
        
        # 2. Submit for approval (only if it was just drafted)
        if action.status == "Drafted":
            action = replenishment_workflow.submit_for_approval(db, action.action_id)
        
        return action
        
    except Exception as e:
        logger.error(f"Failed to process recommendation for {rec.material_id}: {str(e)}")
        return None

def process_single_material(db: Session, material_id: str, plant_id: str, suggested_qty_override: int | None = None) -> ReplenishmentAction | None:
    repo = get_repository()
    rec = replenishment.recommend_for_material(repo, material_id, plant_id)
    if not rec:
        return None
    if suggested_qty_override is not None:
        rec.recommended_qty = suggested_qty_override
    return process_single_recommendation(db, repo, rec)

def process_at_risk_materials(db: Session, top_n: int = 20) -> list[ReplenishmentAction]:
    repo = get_repository()
    recommendations = replenishment.draft_recommendations(repo, top_n=top_n)
    
    actions_processed = []
    for rec in recommendations:
        action = process_single_recommendation(db, repo, rec)
        if action:
            actions_processed.append(action)
            
    return actions_processed

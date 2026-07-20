from datetime import timezone
import uuid
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from models.schemas import ReplenishmentRecommendation, ReplenishmentAction
from persistence import repository

logger = logging.getLogger(__name__)

def create_action_from_recommendation(db: Session, rec: ReplenishmentRecommendation) -> tuple[ReplenishmentAction, bool]:
    existing_action = repository.get_active_action_for_material(db, rec.material_id, rec.plant_id)
    if existing_action:
        logger.info(f"Deduplicated recommendation for material {rec.material_id} at plant {rec.plant_id}. Existing action: {existing_action.action_id}")
        return existing_action, False

    action_id = str(uuid.uuid4())
    token = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    new_action = ReplenishmentAction(
        action_id=action_id,
        material_id=rec.material_id,
        plant_id=rec.plant_id,
        recommended_action=rec.recommended_action,
        recommended_qty=rec.recommended_qty,
        suggested_supplier_id=rec.suggested_supplier_id,
        priority_score=rec.priority_score,
        rationale=rec.rationale,
        status="Drafted",
        approval_token=token,
        created_at=now,
        updated_at=now
    )
    
    action = repository.create_action(db, new_action)
    return action, True

def submit_for_approval(db: Session, action_id: str) -> ReplenishmentAction:
    action = repository.get_action(db, action_id)
    if not action:
        raise ValueError(f"Action {action_id} not found")
    if action.status != "Drafted":
        raise ValueError(f"Action {action_id} cannot be submitted for approval from status {action.status}")
    
    updated_action = repository.update_action_status(db, action_id, "PendingApproval", note="Submitted for approval")
    
    from data.repository import get_repository
    from analytics.health_classification import get_material_health
    from services import notification_service

    repo = get_repository()
    health = get_material_health(repo, updated_action.material_id, updated_action.plant_id)

    if health:
        try:
            repository.update_email_status(db, updated_action.action_id, "Sending")
            success = notification_service.send_replenishment_notification(updated_action, health)
            if success:
                updated_action = repository.mark_notified(db, updated_action.action_id)
                updated_action = repository.update_email_status(db, updated_action.action_id, "Sent")
            else:
                updated_action = repository.update_email_status(db, updated_action.action_id, "Failed")
        except Exception as e:
            repository.update_email_status(db, updated_action.action_id, "Failed")
            raise e

    return updated_action

def approve(db: Session, action_id: str, decided_by: str = "email-link", note: str = None) -> ReplenishmentAction:
    action = repository.get_action(db, action_id)
    if not action:
        raise ValueError(f"Action {action_id} not found")
    if action.status != "PendingApproval":
        raise ValueError(f"Action {action_id} cannot be approved from status {action.status}")
    
    approval_note = f"Approved by {decided_by}"
    if note:
        approval_note += f": {note}"
        
    return repository.update_action_status(db, action_id, "Approved", note=approval_note)

def reject(db: Session, action_id: str, decided_by: str = "email-link", note: str = None) -> ReplenishmentAction:
    action = repository.get_action(db, action_id)
    if not action:
        raise ValueError(f"Action {action_id} not found")
    if action.status != "PendingApproval":
        raise ValueError(f"Action {action_id} cannot be rejected from status {action.status}")
    
    rejection_note = f"Rejected by {decided_by}"
    if note:
        rejection_note += f": {note}"
        
    return repository.update_action_status(db, action_id, "Rejected", note=rejection_note)

def mark_executed(db: Session, action_id: str, note: str = None) -> ReplenishmentAction:
    action = repository.get_action(db, action_id)
    if not action:
        raise ValueError(f"Action {action_id} not found")
    if action.status != "Approved":
        raise ValueError(f"Action {action_id} cannot be executed from status {action.status}")
    
    return repository.update_action_status(db, action_id, "Executed", note=note)

def mark_failed(db: Session, action_id: str, note: str) -> ReplenishmentAction:
    action = repository.get_action(db, action_id)
    if not action:
        raise ValueError(f"Action {action_id} not found")
    if action.status != "Approved":
        raise ValueError(f"Action {action_id} cannot be marked failed from status {action.status}")
        
    return repository.update_action_status(db, action_id, "Failed", note=note)

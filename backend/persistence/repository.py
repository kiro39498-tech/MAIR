from datetime import timezone
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from persistence.models import ReplenishmentActionModel, ReplenishmentActionHistoryModel
from models.schemas import ReplenishmentAction

def _to_pydantic(db_obj: ReplenishmentActionModel) -> ReplenishmentAction:
    return ReplenishmentAction(
        action_id=db_obj.action_id,
        material_id=db_obj.material_id,
        plant_id=db_obj.plant_id,
        recommended_action=db_obj.recommended_action,
        recommended_qty=db_obj.recommended_qty,
        suggested_supplier_id=db_obj.suggested_supplier_id,
        priority_score=db_obj.priority_score,
        rationale=db_obj.rationale,
        status=db_obj.status,
        approval_token=db_obj.approval_token,
        notified_at=db_obj.notified_at,
        email_send_status=db_obj.email_send_status,
        decided_at=db_obj.decided_at,
        decision_note=db_obj.decision_note,
        created_at=db_obj.created_at,
        updated_at=db_obj.updated_at
    )

def create_action(db: Session, action: ReplenishmentAction) -> ReplenishmentAction:
    db_action = ReplenishmentActionModel(
        action_id=action.action_id,
        material_id=action.material_id,
        plant_id=action.plant_id,
        recommended_action=action.recommended_action,
        recommended_qty=action.recommended_qty,
        suggested_supplier_id=action.suggested_supplier_id,
        priority_score=action.priority_score,
        rationale=action.rationale,
        status=action.status,
        approval_token=action.approval_token,
        notified_at=action.notified_at,
        email_send_status=action.email_send_status,
        decided_at=action.decided_at,
        decision_note=action.decision_note,
        created_at=action.created_at,
        updated_at=action.updated_at
    )
    db.add(db_action)
    db.commit()
    db.refresh(db_action)
    return _to_pydantic(db_action)

def get_action(db: Session, action_id: str) -> Optional[ReplenishmentAction]:
    db_action = db.query(ReplenishmentActionModel).filter(ReplenishmentActionModel.action_id == action_id).first()
    if db_action:
        return _to_pydantic(db_action)
    return None

def get_action_by_token(db: Session, token: str) -> Optional[ReplenishmentAction]:
    db_action = db.query(ReplenishmentActionModel).filter(ReplenishmentActionModel.approval_token == token).first()
    if db_action:
        return _to_pydantic(db_action)
    return None

def list_actions(db: Session, status: Optional[str] = None) -> List[ReplenishmentAction]:
    query = db.query(ReplenishmentActionModel)
    if status:
        query = query.filter(ReplenishmentActionModel.status == status)
    return [_to_pydantic(item) for item in query.all()]

def get_active_action_for_material(db: Session, material_id: str, plant_id: str) -> Optional[ReplenishmentAction]:
    db_action = db.query(ReplenishmentActionModel).filter(
        ReplenishmentActionModel.material_id == material_id,
        ReplenishmentActionModel.plant_id == plant_id,
        ReplenishmentActionModel.status.in_(["Drafted", "PendingApproval", "Approved"])
    ).first()
    if db_action:
        return _to_pydantic(db_action)
    return None

def update_action_status(db: Session, action_id: str, new_status: str, note: Optional[str] = None) -> Optional[ReplenishmentAction]:
    db_action = db.query(ReplenishmentActionModel).filter(ReplenishmentActionModel.action_id == action_id).first()
    if not db_action:
        return None

    old_status = db_action.status
    db_action.status = new_status
    if note:
        db_action.decision_note = note

    if new_status in ["Approved", "Rejected", "Executed", "Failed"]:
        db_action.decided_at = datetime.now(timezone.utc)

    # Create history entry
    history_entry = ReplenishmentActionHistoryModel(
        action_id=action_id,
        from_status=old_status,
        to_status=new_status,
        note=note,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(history_entry)
    
    db.commit()
    db.refresh(db_action)
    return _to_pydantic(db_action)

def mark_notified(db: Session, action_id: str) -> Optional[ReplenishmentAction]:
    db_action = db.query(ReplenishmentActionModel).filter(ReplenishmentActionModel.action_id == action_id).first()
    if not db_action:
        return None
    db_action.notified_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_action)
    return _to_pydantic(db_action)

def update_email_status(db: Session, action_id: str, email_status: str) -> Optional[ReplenishmentAction]:
    db_action = db.query(ReplenishmentActionModel).filter(ReplenishmentActionModel.action_id == action_id).first()
    if not db_action:
        return None
    db_action.email_send_status = email_status
    db.commit()
    db.refresh(db_action)
    return _to_pydantic(db_action)

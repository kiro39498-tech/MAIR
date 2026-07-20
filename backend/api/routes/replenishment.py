from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import Optional, List

from persistence.db import get_db
from config.settings import settings
from models.schemas import ReplenishmentAction, CreateActionRequest
from services import replenishment_orchestration, replenishment_workflow, execution_service
from persistence import repository

router = APIRouter(prefix="/api/replenishment", tags=["replenishment"])

@router.post("/actions/create", response_model=ReplenishmentAction)
def create_action(req: CreateActionRequest, db: Session = Depends(get_db)):
    action = replenishment_orchestration.process_single_material(db, req.material_id, req.plant_id, req.suggested_qty_override)
    if not action:
        raise HTTPException(status_code=400, detail="Failed to create action or no recommendation needed.")
    return action

@router.post("/run", response_model=List[ReplenishmentAction])
def run_replenishment(top_n: int = 20, db: Session = Depends(get_db)):
    return replenishment_orchestration.process_at_risk_materials(db, top_n=top_n)

@router.get("/actions", response_model=List[ReplenishmentAction])
def list_actions(status: Optional[str] = None, db: Session = Depends(get_db)):
    return repository.list_actions(db, status=status)

@router.get("/actions/{action_id}", response_model=ReplenishmentAction)
def get_action(action_id: str, db: Session = Depends(get_db)):
    action = repository.get_action(db, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return action

@router.get("/actions/{action_id}/approve")
def approve_action(action_id: str, token: str, db: Session = Depends(get_db)):
    action = repository.get_action(db, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
        
    if action.approval_token != token:
        raise HTTPException(status_code=403, detail="Invalid token")
        
    if action.status in ("Approved", "Rejected", "Executed", "Failed"):
        # If already decided, just redirect them to the frontend dashboard.
        return Response(status_code=302, headers={"Location": f"{settings.frontend_base_url}/recommendations"})
        
    if action.status != "PendingApproval":
        raise HTTPException(status_code=400, detail=f"Action cannot be approved from status {action.status}")
        
    try:
        replenishment_workflow.approve(db, action_id)
        return Response(status_code=302, headers={"Location": f"{settings.frontend_base_url}/recommendations"})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/actions/{action_id}/reject")
def reject_action(action_id: str, token: str, db: Session = Depends(get_db)):
    action = repository.get_action(db, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
        
    if action.approval_token != token:
        raise HTTPException(status_code=403, detail="Invalid token")
        
    if action.status in ("Approved", "Rejected", "Executed", "Failed"):
        return Response(status_code=302, headers={"Location": f"{settings.frontend_base_url}/recommendations"})
        
    if action.status != "PendingApproval":
        raise HTTPException(status_code=400, detail=f"Action cannot be rejected from status {action.status}")
        
    try:
        replenishment_workflow.reject(db, action_id)
        return Response(status_code=302, headers={"Location": f"{settings.frontend_base_url}/recommendations"})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/actions/{action_id}/execute", response_model=ReplenishmentAction)
def execute_action(action_id: str, db: Session = Depends(get_db)):
    try:
        action = execution_service.execute_approved_action(db, action_id)
        return action
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

import logging
from sqlalchemy.orm import Session
from persistence import repository
from services import replenishment_workflow
from connectors.execution_connector import get_execution_connector

logger = logging.getLogger(__name__)

def execute_approved_action(db: Session, action_id: str):
    action = repository.get_action(db, action_id)
    if not action:
        raise ValueError(f"Action {action_id} not found")
        
    if action.status != "Approved":
        raise ValueError(f"Cannot execute action {action_id} from status {action.status}")
        
    connector = get_execution_connector()
    
    # We only handle "Replenish" or "Restore Safety Stock" that have supplier & qty
    if not action.suggested_supplier_id or not action.recommended_qty:
        # For this scope, if it's missing supplier or qty, fail it
        replenishment_workflow.mark_failed(db, action_id, note="Missing supplier or quantity for PO creation")
        raise ValueError("Missing supplier or quantity for PO creation")
        
    try:
        po_id = connector.create_purchase_order(
            material_id=action.material_id,
            plant_id=action.plant_id,
            supplier_id=action.suggested_supplier_id,
            qty=action.recommended_qty
        )
        return replenishment_workflow.mark_executed(db, action_id, note=f"Created {po_id}")
    except Exception as e:
        logger.error(f"Execution failed for {action_id}: {str(e)}")
        replenishment_workflow.mark_failed(db, action_id, note=str(e))
        raise

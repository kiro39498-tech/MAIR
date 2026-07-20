import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from persistence.db import Base
from models.schemas import ReplenishmentRecommendation
from services import replenishment_workflow

# Setup in-memory sqlite DB for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True)
def mock_notification_service():
    with patch("services.notification_service.send_replenishment_notification", return_value=True) as mock_send:
        yield mock_send

@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_workflow_happy_path(db):
    rec = ReplenishmentRecommendation(
        material_id="MAT-HAPPY",
        plant_id="PL-01",
        recommended_action="Replenish",
        recommended_qty=50,
        suggested_supplier_id="SUP-01",
        priority_score=0.8,
        rationale="Low stock"
    )
    
    # Create
    action, _ = replenishment_workflow.create_action_from_recommendation(db, rec)
    assert action.status == "Drafted"
    action_id = action.action_id
    
    # Submit
    action = replenishment_workflow.submit_for_approval(db, action_id)
    assert action.status == "PendingApproval"
    
    # Approve
    action = replenishment_workflow.approve(db, action_id, note="Looks good")
    assert action.status == "Approved"
    
    # Execute
    action = replenishment_workflow.mark_executed(db, action_id, note="Executed successfully")
    assert action.status == "Executed"

def test_workflow_idempotency_guardrail(db):
    rec = ReplenishmentRecommendation(
        material_id="MAT-IDEM",
        plant_id="PL-01",
        recommended_action="Replenish",
        recommended_qty=50,
        priority_score=0.8,
        rationale="Low stock"
    )
    
    # Create first action
    action1, _ = replenishment_workflow.create_action_from_recommendation(db, rec)
    assert action1.status == "Drafted"
    
    # Attempt to create again - should return existing
    action2, _ = replenishment_workflow.create_action_from_recommendation(db, rec)
    assert action1.action_id == action2.action_id
    assert action2.status == "Drafted"
    
    # Transition first action to PendingApproval
    replenishment_workflow.submit_for_approval(db, action1.action_id)
    
    # Attempt to create again - should still return existing
    action3, _ = replenishment_workflow.create_action_from_recommendation(db, rec)
    assert action1.action_id == action3.action_id
    assert action3.status == "PendingApproval"

    # Transition to Approved
    replenishment_workflow.approve(db, action1.action_id)
    
    # Attempt to create again - should still return existing
    action4, _ = replenishment_workflow.create_action_from_recommendation(db, rec)
    assert action1.action_id == action4.action_id
    assert action4.status == "Approved"
    
    # Transition to Executed
    replenishment_workflow.mark_executed(db, action1.action_id)
    
    # Now it should create a new action, because previous is Executed
    action5, _ = replenishment_workflow.create_action_from_recommendation(db, rec)
    assert action5.action_id != action1.action_id
    assert action5.status == "Drafted"

def test_workflow_execute_without_approval_guardrail(db):
    rec = ReplenishmentRecommendation(
        material_id="MAT-GUARD",
        plant_id="PL-01",
        recommended_action="Replenish",
        recommended_qty=50,
        priority_score=0.8,
        rationale="Low stock"
    )
    
    action, _ = replenishment_workflow.create_action_from_recommendation(db, rec)
    assert action.status == "Drafted"
    
    # Cannot execute Drafted
    with pytest.raises(ValueError, match="cannot be executed from status Drafted"):
        replenishment_workflow.mark_executed(db, action.action_id)
        
    replenishment_workflow.submit_for_approval(db, action.action_id)
    
    # Cannot execute PendingApproval
    with pytest.raises(ValueError, match="cannot be executed from status PendingApproval"):
        replenishment_workflow.mark_executed(db, action.action_id)
        
    # Once approved, can execute
    replenishment_workflow.approve(db, action.action_id)
    action_executed = replenishment_workflow.mark_executed(db, action.action_id)
    assert action_executed.status == "Executed"

def test_workflow_reject_path(db):
    rec = ReplenishmentRecommendation(
        material_id="MAT-REJ",
        plant_id="PL-01",
        recommended_action="Replenish",
        recommended_qty=50,
        priority_score=0.8,
        rationale="Low stock"
    )
    
    action, _ = replenishment_workflow.create_action_from_recommendation(db, rec)
    replenishment_workflow.submit_for_approval(db, action.action_id)
    
    action_rejected = replenishment_workflow.reject(db, action.action_id, note="Not needed")
    assert action_rejected.status == "Rejected"
    
    # Cannot execute Rejected
    with pytest.raises(ValueError, match="cannot be executed from status Rejected"):
        replenishment_workflow.mark_executed(db, action.action_id)

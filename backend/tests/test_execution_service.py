import pytest
import os
import hashlib
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from persistence.db import Base
from models.schemas import ReplenishmentRecommendation
from services import replenishment_workflow, execution_service
from config.settings import settings
import persistence.models # Ensure models are registered

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
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

def _get_po_csv_hash():
    original_po_path = os.path.join(settings.csv_data_dir, "purchase_orders.csv")
    with open(original_po_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def test_execution_service(db):
    original_hash = _get_po_csv_hash()
    
    rec = ReplenishmentRecommendation(
        material_id="MAT-EXEC-1",
        plant_id="PL-01",
        recommended_action="Replenish",
        recommended_qty=100,
        suggested_supplier_id="SUP-01",
        priority_score=0.9,
        rationale="Low stock"
    )
    
    # Drafted
    action, _ = replenishment_workflow.create_action_from_recommendation(db, rec)
    
    # 1. Test Drafted execution fails
    with pytest.raises(ValueError, match="Cannot execute action"):
        execution_service.execute_approved_action(db, action.action_id)
        
    # PendingApproval
    replenishment_workflow.submit_for_approval(db, action.action_id)
    
    # 2. Test PendingApproval execution fails
    with pytest.raises(ValueError, match="Cannot execute action"):
        execution_service.execute_approved_action(db, action.action_id)
        
    # Approved
    replenishment_workflow.approve(db, action.action_id)
    
    created_file = os.path.join(settings.csv_data_dir, "purchase_orders_created.csv")
    
    # Measure line count in created_file before
    before_count = 0
    if os.path.exists(created_file):
        with open(created_file, 'r', encoding='utf-8') as f:
            before_count = sum(1 for _ in f)
            
    # 3. Test Approved execution succeeds
    executed_action = execution_service.execute_approved_action(db, action.action_id)
    
    assert executed_action.status == "Executed"
    assert "Created PO-EXEC" in executed_action.decision_note
    
    # Check that a row was added
    assert os.path.exists(created_file)
    with open(created_file, 'r', encoding='utf-8') as f:
        after_count = sum(1 for _ in f)
        
    if before_count == 0:
        assert after_count == 2
    else:
        assert after_count == before_count + 1
        
    # 4. Verify original PO CSV is unchanged
    assert _get_po_csv_hash() == original_hash

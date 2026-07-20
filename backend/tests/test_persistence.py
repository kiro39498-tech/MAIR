from datetime import timezone
import pytest
from datetime import datetime
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from persistence.db import Base
from persistence.repository import create_action, get_action, update_action_status
from models.schemas import ReplenishmentAction
from persistence.models import ReplenishmentActionHistoryModel

# Setup in-memory sqlite DB for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_persistence_flow(db):
    action_id = str(uuid.uuid4())
    token = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    # 1. Create an action
    action = ReplenishmentAction(
        action_id=action_id,
        material_id="MAT01",
        plant_id="PL01",
        recommended_action="Replenish",
        recommended_qty=100,
        suggested_supplier_id="SUP01",
        priority_score=0.9,
        rationale="Low stock",
        status="Drafted",
        approval_token=token,
        created_at=now,
        updated_at=now
    )
    
    created_action = create_action(db, action)
    assert created_action.action_id == action_id
    assert created_action.status == "Drafted"
    
    # 2. Verify it's retrievable
    fetched_action = get_action(db, action_id)
    assert fetched_action is not None
    assert fetched_action.action_id == action_id
    
    # 3. Transition: Drafted -> PendingApproval
    updated_1 = update_action_status(db, action_id, "PendingApproval", note="Sent for approval")
    assert updated_1.status == "PendingApproval"
    
    # Transition: PendingApproval -> Approved
    updated_2 = update_action_status(db, action_id, "Approved", note="Approved by manager")
    assert updated_2.status == "Approved"
    
    # 4. Assert the history table has exactly 2 rows
    history_records = db.query(ReplenishmentActionHistoryModel).filter(ReplenishmentActionHistoryModel.action_id == action_id).order_by(ReplenishmentActionHistoryModel.id).all()
    assert len(history_records) == 2
    
    assert history_records[0].from_status == "Drafted"
    assert history_records[0].to_status == "PendingApproval"
    assert history_records[0].note == "Sent for approval"
    
    assert history_records[1].from_status == "PendingApproval"
    assert history_records[1].to_status == "Approved"
    assert history_records[1].note == "Approved by manager"

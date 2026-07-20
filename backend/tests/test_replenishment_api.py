import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.main import app
from persistence.db import Base, get_db
import persistence.models  # Ensure models are registered

from sqlalchemy.pool import StaticPool
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

@patch("services.notification_service.send_replenishment_notification")
def test_replenishment_api_flow(mock_send):
    mock_send.return_value = True

    # 1. POST /run
    response = client.post("/api/replenishment/run?top_n=5")
    assert response.status_code == 200
    actions = response.json()
    assert isinstance(actions, list)
    assert len(actions) > 0  # Assuming the actual dataset yields some at-risk materials

    # Grab the first action
    first_action = actions[0]
    action_id = first_action["action_id"]
    token = first_action["approval_token"]
    
    # 2. GET /actions to confirm it's there
    resp_actions = client.get("/api/replenishment/actions")
    assert resp_actions.status_code == 200
    assert any(a["action_id"] == action_id for a in resp_actions.json())

    # 3. GET /actions/{action_id} to confirm detail view
    resp_action = client.get(f"/api/replenishment/actions/{action_id}")
    assert resp_action.status_code == 200
    assert resp_action.json()["status"] == "PendingApproval"  # Since process_at_risk_materials submits them

    # 4. Approve link with wrong token
    bad_approve = client.get(f"/api/replenishment/actions/{action_id}/approve?token=wrong")
    assert bad_approve.status_code == 403

    # 5. Approve link with correct token
    approve = client.get(f"/api/replenishment/actions/{action_id}/approve?token={token}", follow_redirects=False)
    assert approve.status_code == 302
    
    # 6. Check that status is Approved
    resp_action2 = client.get(f"/api/replenishment/actions/{action_id}")
    assert resp_action2.json()["status"] == "Approved"
    
    # Let's get the DB to check history count before re-hitting
    db = TestingSessionLocal()
    try:
        from persistence.models import ReplenishmentActionHistoryModel
        history_count_before = db.query(ReplenishmentActionHistoryModel).filter_by(action_id=action_id).count()
    finally:
        db.close()

    # 6. Hit approve again -> Should not error, but say "already Approved"
    approve_again = client.get(f"/api/replenishment/actions/{action_id}/approve?token={token}", follow_redirects=False)
    assert approve_again.status_code == 302
    
    # 7. Hit reject on the approved action -> Should say "already Approved", not reject it
    reject_after_approve = client.get(f"/api/replenishment/actions/{action_id}/reject?token={token}", follow_redirects=False)
    assert reject_after_approve.status_code == 302
    
    # Verify no new history rows were created by those duplicate hits
    db = TestingSessionLocal()
    try:
        history_count_after = db.query(ReplenishmentActionHistoryModel).filter_by(action_id=action_id).count()
        assert history_count_before == history_count_after, "Duplicate decision endpoints mutated the audit trail"
    finally:
        db.close()


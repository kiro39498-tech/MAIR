import pytest
from unittest.mock import patch
from sqlalchemy.orm import Session

from persistence.db import Base
import persistence.models # Important for Base.metadata to discover tables
from tests.test_replenishment_api import TestingSessionLocal, engine
from services import replenishment_orchestration

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@patch("services.notification_service.send_replenishment_notification")
def test_deduplication_orchestration(mock_notify):
    mock_notify.return_value = True
    db = TestingSessionLocal()
    try:
        # 1. Run first time
        actions1 = replenishment_orchestration.process_at_risk_materials(db, top_n=5)
        # Verify notification was called
        call_count_1 = mock_notify.call_count
        assert call_count_1 > 0
        
        # 2. Run second time against same dataset
        actions2 = replenishment_orchestration.process_at_risk_materials(db, top_n=5)
        
        # The number of actions processed should be the same
        assert len(actions1) == len(actions2)
        
        # BUT the notification should NOT be called again
        assert mock_notify.call_count == call_count_1
        
    finally:
        db.close()

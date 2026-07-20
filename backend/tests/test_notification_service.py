from datetime import timezone
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from config.settings import settings
from models.schemas import ReplenishmentAction, MaterialHealth
from services.notification_service import should_notify, send_replenishment_notification


def test_should_notify():
    # It should only notify for Shortage by default
    assert should_notify("Shortage") is True
    assert should_notify("Healthy") is False
    assert should_notify("Excess") is False


@patch("services.notification_service.smtplib.SMTP")
def test_send_replenishment_notification_success(mock_smtp):
    # Setup mock SMTP
    mock_smtp_instance = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
    
    # Temporarily set valid configuration
    original_to = settings.notify_email_to
    original_from = settings.notify_email_from
    original_user = settings.smtp_username
    original_pass = settings.smtp_password
    
    settings.notify_email_to = "admin@example.com"
    settings.notify_email_from = "bot@example.com"
    settings.smtp_username = "user"
    settings.smtp_password = "password"

    try:
        now = datetime.now(timezone.utc)
        action = ReplenishmentAction(
            action_id="act-123",
            material_id="MAT01",
            plant_id="PL01",
            recommended_action="Replenish",
            recommended_qty=100,
            suggested_supplier_id="SUP01",
            priority_score=0.9,
            rationale="Stock critically low",
            status="Drafted",
            approval_token="secret-token-abc",
            created_at=now,
            updated_at=now
        )
        
        health = MaterialHealth(
            material_id="MAT01",
            plant_id="PL01",
            usable_qty=10,
            safety_stock_qty=20,
            reorder_point_qty=30,
            max_stock_qty=100,
            status="Shortage",
            reason="Below safety stock"
        )

        result = send_replenishment_notification(action, health)
        assert result is True
        
        # Verify SMTP calls
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with("user", "password")
        mock_smtp_instance.sendmail.assert_called_once()
        
        # Extract sent message
        args, kwargs = mock_smtp_instance.sendmail.call_args
        msg_str = args[2]
        
        # Verify contents (look for the href in the HTML body)
        assert f'href="{settings.api_base_url}/api/replenishment/actions/act-123/approve?token=secret-token-abc"' in msg_str
        assert f'href="{settings.api_base_url}/api/replenishment/actions/act-123/reject?token=secret-token-abc"' in msg_str
        assert "Subject: [MAT01] [PL01] ACTION REQUIRED: Material Shortage" in msg_str

    finally:
        # Restore configuration
        settings.notify_email_to = original_to
        settings.notify_email_from = original_from
        settings.smtp_username = original_user
        settings.smtp_password = original_pass


def test_send_replenishment_notification_missing_config():
    # Temporarily remove configuration
    original_to = settings.notify_email_to
    settings.notify_email_to = None

    try:
        now = datetime.now(timezone.utc)
        action = ReplenishmentAction(
            action_id="act-123",
            material_id="MAT01",
            plant_id="PL01",
            recommended_action="Replenish",
            priority_score=0.9,
            rationale="Stock critically low",
            status="Drafted",
            approval_token="secret-token-abc",
            created_at=now,
            updated_at=now
        )
        
        health = MaterialHealth(
            material_id="MAT01",
            plant_id="PL01",
            usable_qty=10,
            safety_stock_qty=20,
            reorder_point_qty=30,
            max_stock_qty=100,
            status="Shortage",
            reason="Below safety stock"
        )
        
        # Should return False instead of attempting to send
        result = send_replenishment_notification(action, health)
        assert result is False

    finally:
        settings.notify_email_to = original_to


@patch("services.notification_service.smtplib.SMTP")
def test_send_replenishment_notification_exception_propagation(mock_smtp):
    # Setup mock SMTP to throw an exception
    mock_smtp_instance = MagicMock()
    mock_smtp_instance.login.side_effect = Exception("SMTP Auth Failed")
    mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
    
    original_to = settings.notify_email_to
    original_from = settings.notify_email_from
    original_user = settings.smtp_username
    original_pass = settings.smtp_password
    
    settings.notify_email_to = "admin@example.com"
    settings.notify_email_from = "bot@example.com"
    settings.smtp_username = "user"
    settings.smtp_password = "password"

    try:
        now = datetime.now(timezone.utc)
        action = ReplenishmentAction(
            action_id="act-123",
            material_id="MAT01",
            plant_id="PL01",
            recommended_action="Replenish",
            recommended_qty=100,
            suggested_supplier_id="SUP01",
            priority_score=0.9,
            rationale="Stock critically low",
            status="Drafted",
            approval_token="secret-token-abc",
            created_at=now,
            updated_at=now
        )
        
        health = MaterialHealth(
            material_id="MAT01",
            plant_id="PL01",
            usable_qty=10,
            safety_stock_qty=20,
            reorder_point_qty=30,
            max_stock_qty=100,
            status="Shortage",
            reason="Below safety stock"
        )
        
        # Verify the exception propagates
        with pytest.raises(Exception) as exc_info:
            send_replenishment_notification(action, health)
        assert "SMTP Auth Failed" in str(exc_info.value)
        
    finally:
        settings.notify_email_to = original_to
        settings.notify_email_from = original_from
        settings.smtp_username = original_user
        settings.smtp_password = original_pass


@patch("services.notification_service.smtplib.SMTP")
@patch("analytics.health_classification.get_material_health")
def test_submit_for_approval_exception_propagation(mock_health, mock_smtp):
    # Setup mock SMTP to throw an exception
    mock_smtp_instance = MagicMock()
    mock_smtp_instance.login.side_effect = Exception("Connection Refused")
    mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
    
    # Setup mock health to return a MaterialHealth object so we bypass repository/connector dependencies
    from models.schemas import MaterialHealth
    mock_health.return_value = MaterialHealth(
        material_id="MAT01",
        plant_id="PL01",
        usable_qty=10,
        safety_stock_qty=20,
        reorder_point_qty=30,
        max_stock_qty=100,
        status="Shortage",
        reason="Below safety stock"
    )

    original_to = settings.notify_email_to
    original_from = settings.notify_email_from
    original_user = settings.smtp_username
    original_pass = settings.smtp_password
    
    settings.notify_email_to = "admin@example.com"
    settings.notify_email_from = "bot@example.com"
    settings.smtp_username = "user"
    settings.smtp_password = "password"

    # Setup in-memory sqlite DB for test
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from persistence.db import Base
    from services import replenishment_workflow
    from persistence import repository

    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    try:
        now = datetime.now(timezone.utc)
        action = ReplenishmentAction(
            action_id="act-123",
            material_id="MAT01",
            plant_id="PL01",
            recommended_action="Replenish",
            recommended_qty=100,
            suggested_supplier_id="SUP01",
            priority_score=0.9,
            rationale="Stock critically low",
            status="Drafted",
            approval_token="secret-token-abc",
            created_at=now,
            updated_at=now
        )
        repository.create_action(db, action)
        
        # Verify submit_for_approval propagates SMTP exception and sets status to Failed
        with pytest.raises(Exception) as exc_info:
            replenishment_workflow.submit_for_approval(db, "act-123")
            
        assert "Connection Refused" in str(exc_info.value)
        
        # Verify DB action reflects "Failed" email status
        db_action = repository.get_action(db, "act-123")
        assert db_action.email_send_status == "Failed"
        assert db_action.status == "PendingApproval"

    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        settings.notify_email_to = original_to
        settings.notify_email_from = original_from
        settings.smtp_username = original_user
        settings.smtp_password = original_pass


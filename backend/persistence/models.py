from datetime import timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from persistence.db import Base
from datetime import datetime

class ReplenishmentActionModel(Base):
    __tablename__ = "replenishment_actions"

    action_id = Column(String, primary_key=True, index=True)
    material_id = Column(String, index=True, nullable=False)
    plant_id = Column(String, index=True, nullable=False)
    recommended_action = Column(String, nullable=False)
    recommended_qty = Column(Integer, nullable=True)
    suggested_supplier_id = Column(String, nullable=True)
    priority_score = Column(Float, nullable=False)
    rationale = Column(String, nullable=False)
    status = Column(String, nullable=False, index=True)
    approval_token = Column(String, nullable=False, unique=True, index=True)
    notified_at = Column(DateTime, nullable=True)
    email_send_status = Column(String, nullable=True)
    decided_at = Column(DateTime, nullable=True)
    decision_note = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    history = relationship("ReplenishmentActionHistoryModel", back_populates="action", cascade="all, delete-orphan")


class ReplenishmentActionHistoryModel(Base):
    __tablename__ = "replenishment_action_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    action_id = Column(String, ForeignKey("replenishment_actions.action_id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    from_status = Column(String, nullable=True)
    to_status = Column(String, nullable=False)
    note = Column(String, nullable=True)

    action = relationship("ReplenishmentActionModel", back_populates="history")

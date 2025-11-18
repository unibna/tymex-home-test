from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import(
    Column,
    DateTime,
    Enum as SQLAlchemyEnum,
    Numeric,
    event,
    ForeignKey,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates, relationship

from app.core.database import Base


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID, primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)

    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(SQLAlchemyEnum(PaymentStatus, name="payment_status", create_type=False), nullable=False, default=PaymentStatus.PENDING)

    idempotency_key = Column(UUID, ForeignKey("idempotency_keys.key"), nullable=False)
    idempotency = relationship("IdempotencyKey", back_populates="payment", foreign_keys=[idempotency_key])

    @validates("amount")
    def validate_amount(self, _, value) -> Numeric:
        if value is None:
            raise ValueError("Amount is required")
        if value <= 0:
            raise ValueError("Amount must be greater than 0")
        return value
    
    @validates("status")
    def validate_status(self, _, value) -> PaymentStatus:
        if value is None:
            raise ValueError("Status is required")
        if value not in PaymentStatus:
            raise ValueError("Invalid status")
        return value




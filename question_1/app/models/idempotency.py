from enum import Enum

from sqlalchemy import (
    Column,
    DateTime,
    String,
    Enum as SQLAlchemyEnum,
    ForeignKey,
    JSON,
    func,
    event,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class IdempotencyKeyStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    key = Column(UUID, primary_key=True, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    request_hash = Column(String(128), nullable=False)
    response_body = Column(JSON, nullable=True)

    status = Column(
        SQLAlchemyEnum(IdempotencyKeyStatus, name="idempotency_key_status", create_type=False),
        default=IdempotencyKeyStatus.PENDING
    )

    expires_at = Column(DateTime, nullable=False)
    
    payment = relationship("Payment", back_populates="idempotency", uselist=False)



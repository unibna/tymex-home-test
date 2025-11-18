from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.payment import PaymentStatus


class PaymentCreate(BaseModel):
    amount: float


class Payment(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    amount: float
    status: PaymentStatus

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.apis.deps import get_idempotency_key
from app.core.database import get_session
from app.operations.create_payment_operation import CreatePaymentOperation
from app.schemas.payment import PaymentCreate

logger = logging.getLogger(__name__)

payment_router = APIRouter()


@payment_router.post("", status_code=status.HTTP_201_CREATED)
async def create_payment(
    request_body: PaymentCreate,
    session: AsyncSession = Depends(get_session),
    idempotency_key: UUID = Depends(get_idempotency_key),
):
    try:
        operation = CreatePaymentOperation(session, idempotency_key, request_body)
        await operation.execute()
    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))



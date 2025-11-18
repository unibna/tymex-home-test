import asyncio
import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.idempotency import IdempotencyKeyStatus
from app.models.payment import Payment, PaymentStatus
from app.schemas.payment import PaymentCreate, PaymentSerializer
from app.services.idempotency_service import IdempotencyKeyService

logger = logging.getLogger(__name__)


class CreatePaymentOperation:

    def __init__(self, db: AsyncSession, idempotency_key: UUID, request_body: PaymentCreate):
        self.db = db
        self.request_idempotency_key = idempotency_key
        self.request_body = request_body

    async def execute(self) -> PaymentSerializer:
        service = IdempotencyKeyService(self.db, self.request_idempotency_key)
        
        idempotency_key = await service.load_or_create(self.request_body.model_dump())

        if idempotency_key.status == IdempotencyKeyStatus.COMPLETED:
            response = PaymentSerializer.model_validate(idempotency_key.response_body).model_dump(mode='json')
            return response

        if idempotency_key.status == IdempotencyKeyStatus.IN_PROGRESS:
            raise Exception("Request is currently being processed")

        acquired = await service.acquire_lock()
        if not acquired:
            raise Exception("Request is currently being processed")

        try:
            await service.mark_processing()

            payment = await self._create_payment()
            await self._process_payment(payment)

            response = PaymentSerializer(
                id=payment.id,
                created_at=payment.created_at,
                updated_at=payment.updated_at,
                deleted_at=payment.deleted_at,
                amount=float(payment.amount),
                status=payment.status
            ).model_dump(mode='json')

            await service.mark_completed(response)

            return response

        except Exception as e:
            try:
                await service.mark_failed()
            except Exception:
                logger.error("Failed to mark idempotency key as failed", exc_info=True)
            raise Exception(f"Failed to create payment: {e}")

        finally:
            await service.release_lock()

    async def _create_payment(self):
        payment = Payment(
            amount=self.request_body.amount,
            status=PaymentStatus.PENDING,
            idempotency_key=self.request_idempotency_key,
        )
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        return payment
    
    async def _process_payment(self, payment: Payment):
        """
        Simulate the payment processing by sending a request to the payment gateway.
        """
        logger.info(f"Simulating payment processing for payment {payment.id} for 10 seconds")
        await asyncio.sleep(10)



from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.idempotency import IdempotencyKeyStatus
from app.models.payment import Payment as PaymentModel, PaymentStatus
from app.schemas.payment import PaymentCreate, Payment as PaymentSchema
from app.services.idempotency_service import IdempotencyKeyService


class CreatePaymentOperation:

    def __init__(self, db: AsyncSession, idempotency_key: UUID, request_body: PaymentCreate):
        self.db = db
        self.request_idempotency_key = idempotency_key
        self.request_body = request_body

    async def execute(self):
        service = IdempotencyKeyService(self.db, self.request_idempotency_key)

        idempotency_key = await service.load_or_create(self.request_body.model_dump())

        if idempotency_key.status == IdempotencyKeyStatus.COMPLETED:
            return idempotency_key.response_body

        if idempotency_key.status == IdempotencyKeyStatus.IN_PROGRESS:
            raise Exception("Request is currently being processed")

        acquired = await service.acquire_lock()
        if not acquired:
            raise Exception("Another request is processing this idempotency key")

        try:
            await service.mark_processing()

            payment = await self._create_payment()

            response = PaymentSchema(
                id=payment.id,
                created_at=payment.created_at,
                updated_at=payment.updated_at,
                deleted_at=payment.deleted_at,
                amount=float(payment.amount),
                status=payment.status
            ).model_dump(mode='json')

            await service.mark_completed(response)

            return response

        except Exception:
            await service.mark_failed()
            raise

        finally:
            await service.release_lock()

    async def _create_payment(self):
        payment = PaymentModel(
            amount=self.request_body.amount,
            status=PaymentStatus.PENDING,
            idempotency_key=self.request_idempotency_key,
        )
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        return payment



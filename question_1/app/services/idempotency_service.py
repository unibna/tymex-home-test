from datetime import datetime, timedelta, timezone
import json
import hashlib
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache_client
from app.models.idempotency import IdempotencyKey, IdempotencyKeyStatus


class IdempotencyKeyService:
    LOCK_KEY_TEMPLATE = "idempotency_lock:{key}"
    LOCK_TIMEOUT = 30  # seconds
    EXPIRES_IN_DAYS = 7

    def __init__(self, db: AsyncSession, key: UUID):
        self.db = db
        self.key = key
        self.idempotency_key: IdempotencyKey | None = None

    # ----------------------------------------------------
    # PUBLIC METHODS
    # ----------------------------------------------------

    async def load_or_create(self, request_body: dict) -> IdempotencyKey:
        request_hash = self._compute_request_hash(request_body)

        await self._load()

        if self.idempotency_key:
            if self.idempotency_key.request_hash != request_hash:
                raise Exception("Request body does not match previous request for this idempotency key")
            return self.idempotency_key

        await self._create(request_hash)
        return self.idempotency_key

    async def acquire_lock(self) -> bool:
        lock_key = self.LOCK_KEY_TEMPLATE.format(key=self.key)
        return await cache_client.set(lock_key, "locked", ex=self.LOCK_TIMEOUT, nx=True)

    async def release_lock(self):
        lock_key = self.LOCK_KEY_TEMPLATE.format(key=self.key)
        await cache_client.delete(lock_key)

    async def mark_processing(self):
        self.idempotency_key.status = IdempotencyKeyStatus.IN_PROGRESS
        await self._commit_state()

    async def mark_completed(self, response_body: dict):
        self.idempotency_key.status = IdempotencyKeyStatus.COMPLETED
        self.idempotency_key.response_body = response_body
        await self._commit_state()

    async def mark_failed(self):
        self.idempotency_key.status = IdempotencyKeyStatus.FAILED
        await self._commit_state()

    # ----------------------------------------------------
    # INTERNAL HELPERS
    # ----------------------------------------------------

    async def _load(self):
        result = await self.db.execute(
            select(IdempotencyKey).where(IdempotencyKey.key == self.key)
        )
        self.idempotency_key = result.scalar_one_or_none()

    async def _create(self, request_hash: str):
        # Use timezone-naive UTC datetime to match TIMESTAMP WITHOUT TIME ZONE column
        expires_at = (datetime.now(timezone.utc) + timedelta(days=self.EXPIRES_IN_DAYS)).replace(tzinfo=None)
        self.idempotency_key = IdempotencyKey(
            key=self.key,
            request_hash=request_hash,
            status=IdempotencyKeyStatus.PENDING,
            expires_at=expires_at
        )
        self.db.add(self.idempotency_key)
        await self.db.commit()
        await self.db.refresh(self.idempotency_key)

    async def _commit_state(self):
        self.db.add(self.idempotency_key)
        await self.db.commit()
        await self.db.refresh(self.idempotency_key)

    @staticmethod
    def _compute_request_hash(body: dict) -> str:
        payload = json.dumps(body, sort_keys=True).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()



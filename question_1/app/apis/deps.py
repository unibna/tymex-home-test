from uuid import UUID

from fastapi import Header, HTTPException, status


async def get_idempotency_key(idempotency_key: str = Header(None, alias="Idempotency-Key")):
    if not idempotency_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required header: Idempotency-Key",
        )

    return UUID(idempotency_key)



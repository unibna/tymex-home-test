from fastapi import APIRouter

from app.apis.payment import payment_router


api_router = APIRouter(prefix="/api/v1")

api_router.include_router(payment_router, prefix="/payments", tags=["payments"])



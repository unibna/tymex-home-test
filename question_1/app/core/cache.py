from redis import asyncio as aioredis

from app.core.settings import settings


cache_client = aioredis.from_url(settings.REDIS_URL)



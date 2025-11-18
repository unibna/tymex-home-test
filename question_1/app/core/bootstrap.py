from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.apis.routes import api_router
from app.core.migrations import run_migrations


@asynccontextmanager
async def lifespan(app: FastAPI):
    await run_migrations()
    yield


def init() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    app.include_router(api_router)

    return app



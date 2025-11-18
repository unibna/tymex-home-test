from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.apis.routes import api_router
from app.core.migrations import run_migrations


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Run migrations
    await run_migrations()
    yield
    # Shutdown: (if needed, add cleanup code here)


def init() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    app.include_router(api_router)

    return app



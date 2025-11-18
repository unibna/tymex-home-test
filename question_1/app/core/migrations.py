import asyncio
import logging
from pathlib import Path

from app.core.settings import settings

logger = logging.getLogger(__name__)


async def run_migrations() -> None:
    loop = asyncio.get_event_loop()
    
    def run_alembic_upgrade():
        from alembic import config as alembic_config
        from alembic import command
        
        project_root = Path(__file__).parent.parent.parent
        
        alembic_cfg = alembic_config.Config(str(project_root / "alembic.ini"))
        
        alembic_cfg.set_main_option(
            "sqlalchemy.url",
            f"postgresql+asyncpg://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}"
            f"@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
        )

        try:
            command.upgrade(alembic_cfg, "head")
            logger.info("Database migrations completed successfully")
        except Exception as e:
            logger.error(f"Migration error: {e}")
            raise
    
    await loop.run_in_executor(None, run_alembic_upgrade)


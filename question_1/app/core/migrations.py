import asyncio
from pathlib import Path

from app.core.settings import settings


async def run_migrations() -> None:
    """Run database migrations automatically on startup."""
    # Run Alembic upgrade command asynchronously
    # Alembic's command API is synchronous, so we run it in an executor
    loop = asyncio.get_event_loop()
    
    def run_alembic_upgrade():
        """Run Alembic upgrade command synchronously."""
        from alembic import config as alembic_config
        from alembic import command
        
        # Get the project root directory (where alembic.ini is located)
        project_root = Path(__file__).parent.parent.parent
        
        alembic_cfg = alembic_config.Config(str(project_root / "alembic.ini"))
        
        # Set the database URL
        alembic_cfg.set_main_option(
            "sqlalchemy.url",
            f"postgresql+asyncpg://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}"
            f"@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
        )
        
        # Run migrations
        try:
            command.upgrade(alembic_cfg, "head")
            print("Database migrations completed successfully")
        except Exception as e:
            print(f"Migration error: {e}")
            raise
    
    await loop.run_in_executor(None, run_alembic_upgrade)


import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    
    # Database
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT: int = os.getenv("DATABASE_PORT", 5432)
    DATABASE_USER: str = os.getenv("DATABASE_USER", "postgres")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "postgres")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "postgres")

    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = os.getenv("REDIS_PORT", 6379)
    REDIS_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
settings = Settings()

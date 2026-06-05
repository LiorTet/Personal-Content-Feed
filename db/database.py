import os
import sys
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from core.logger_format import logger


def get_engine_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        if "pytest" in sys.modules or os.getenv("ENV") == "ci":
            logger.info("No DATABASE_URL found. Passing dummy Postgres string for mock test collection.")
            # Use a dummy postgres URL so SQLAlchemy loads the already-present asyncpg driver
            return "postgresql+asyncpg://dummy_user:dummy_pass@localhost:5432/dummy_db"

        logger.critical("DATABASE_URL environment variable is not set.")
        raise SystemExit(1)
    return url


# Create the engine lazily by invoking our context-aware URL manager
DATABASE_URL = get_engine_url()
engine = create_async_engine(DATABASE_URL)

# Configure the sessionmaker factory bound to the live engine instance
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    """Initializes schema migrations and necessary extensions."""
    if os.getenv("ENV") == "ci":
        logger.info("Skipping DB init in CI environment.")
        return

    async with engine.begin() as conn:
        # Enable pgvector extension if we are running against PostgreSQL
        if "postgresql" in engine.url.drivername:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

        # Build relational schemas
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Dependency injection provider for scoping database sessions."""
    async with async_session() as session:
        yield session

import logging
import time
from datetime import UTC, datetime
from typing import Any, AsyncGenerator

from sqlalchemy import Connection, MetaData, Pool, event
from sqlalchemy.engine.interfaces import ExecutionContext
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Mapper, declarative_base

from ..config import get_database_settings

metadata = MetaData()
Base = declarative_base(metadata=metadata)

settings = get_database_settings()
DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=1800,
)
async_session_maker = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


# ─────────────── SYNC ORM LISTENERS ───────────────
# (Must be 'def', use sync 'Connection')


@event.listens_for(Base, "before_insert", propagate=True)
def set_created_at(mapper: Mapper[Any], connection: Connection, target: Any) -> None:
    if hasattr(target, "created_at"):
        if getattr(target, "created_at", None) is None:
            target.created_at = datetime.now(UTC)


@event.listens_for(Base, "before_update", propagate=True)
def set_updated_at(mapper: Mapper[Any], connection: Connection, target: Any) -> None:
    if hasattr(target, "updated_at"):
        target.updated_at = datetime.now(UTC)


# ─────────────── SYNC I/O LISTENERS ───────────────
# (Must be 'def', target 'engine.sync_engine')


@event.listens_for(engine.sync_engine, "before_cursor_execute")
def before_cursor_execute(
    conn: Connection,  # Use sync 'Connection'
    cursor: Any,
    statement: str,
    parameters: Any,
    context: ExecutionContext,
    executemany: bool,
) -> None:
    """Track query start time and log statement preview."""
    setattr(context, "_query_start_time", time.time())
    logging.debug(f"Start Query: {statement[:100]}")


@event.listens_for(engine.sync_engine, "after_cursor_execute")
def after_cursor_execute(
    conn: Connection,
    cursor: Any,
    statement: str,
    parameters: Any,
    context: ExecutionContext,
    executemany: bool,
) -> None:
    """Log query execution duration."""
    total = time.time() - getattr(context, "_query_start_time", time.time())
    logging.debug(f"Query complete in {total:.4f}s")


# ─────────────── SYNC POOL LISTENER ───────────────
# (Must be 'def', target 'engine.pool')


@event.listens_for(engine.pool, "close")
def on_connection_close(dbapi_connection: Any, connection_record: Pool) -> None:
    """Log connection close events."""
    logging.debug("Database connection closed.")

import logging
import time
from datetime import UTC, datetime
from typing import AsyncGenerator

from sqlalchemy import MetaData, event, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

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


@event.listens_for(engine.sync_engine, "engine_connect")
def test_connection(connection, branch):
    if branch:
        return
    try:
        connection.scalar(text("SELECT 1"))
    except Exception as exc:
        logging.error(f"DB connection failed: {exc}")
        raise


@event.listens_for(Base, "before_insert", propagate=True)
def set_created_at(mapper, connection, target):
    if hasattr(target, "created_at"):
        if getattr(target, "created_at", None) is None:
            target.created_at = datetime.now(UTC)


@event.listens_for(Base, "before_update", propagate=True)
def set_updated_at(mapper, connection, target):
    if hasattr(target, "updated_at"):
        target.updated_at = datetime.now(UTC)


@event.listens_for(engine.sync_engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()
    logging.debug(f"Start Query: {statement[:100]}")


@event.listens_for(engine.sync_engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    logging.debug(f"Query complete in {total:.4f}s")


@event.listens_for(engine.sync_engine, "close")
def on_connection_close(dbapi_connection, connection_record):
    logging.debug("Database connection closed.")


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

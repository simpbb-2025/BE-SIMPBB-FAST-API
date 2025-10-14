from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Declarative base for all SQLAlchemy models."""


engine = create_async_engine(
    settings.sqlalchemy_database_uri,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=1800,
    connect_args={"init_command": f"SET time_zone = '{settings.mysql_time_zone}'"},
)

AsyncSessionFactory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async SQLAlchemy session."""

    async with AsyncSessionFactory() as session:
        try:
            yield session
        except Exception:  # pragma: no cover - defensive rollback
            await session.rollback()
            raise
        finally:
            await session.close()

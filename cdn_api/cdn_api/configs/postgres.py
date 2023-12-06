from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)


async_session: async_sessionmaker | None
engine: None | AsyncEngine = None


async def get_db_session() -> AsyncGenerator[None, AsyncSession]:
    global async_session

    if async_session is None:
        raise RuntimeError("SQL client has not been defined.")

    async with async_session() as session:
        yield session

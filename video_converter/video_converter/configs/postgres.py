from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from video_converter.configs.settings import Settings

_async_session: async_sessionmaker | None = None
_engine: None | AsyncEngine = None


async def init_async_engine(settings: Settings) -> None:
    global _engine
    global _async_session

    _engine = create_async_engine(
        settings.postgres_dsn(), echo=settings.debug, future=True
    )
    _async_session = async_sessionmaker(_engine, expire_on_commit=False)


async def close_async_engine() -> None:
    global _engine

    if _engine is None:
        raise RuntimeError("SQL engine has not been defined.")

    await _engine.dispose()


async def get_db_session() -> AsyncGenerator[None, AsyncSession]:
    global _async_session

    if _async_session is None:
        raise RuntimeError("SQL client has not been defined.")

    async with _async_session() as session:
        yield session

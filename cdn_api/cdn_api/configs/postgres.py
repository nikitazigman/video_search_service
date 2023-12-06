from collections.abc import AsyncGenerator

from cdn_api.configs.settings import Settings
from cdn_api.models.common import BaseModel
from cdn_api.models.edge_nodes import EdgeNode, Location  # noqa: F401

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.schema import CreateSchema


_async_session: async_sessionmaker | None
_engine: None | AsyncEngine = None


async def _create_test_db(
    settings: Settings, connection: AsyncConnection
) -> None:
    await connection.execute(
        CreateSchema(
            settings.postgres_schema,
            if_not_exists=True,
        ),
    )
    await connection.run_sync(BaseModel.metadata.drop_all)
    await connection.run_sync(BaseModel.metadata.create_all)


async def init_async_engine(settings: Settings) -> None:
    global _engine
    global _async_session

    _engine = create_async_engine(
        settings.postgres_dsn(), echo=settings.debug, future=True
    )
    _async_session = async_sessionmaker(_engine, expire_on_commit=False)

    if settings.debug:
        async with _engine.begin() as connection:
            await _create_test_db(settings, connection)


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

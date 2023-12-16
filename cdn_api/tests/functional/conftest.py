import asyncio

from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Any, cast

from cdn_api.configs.minio import get_s3_client
from cdn_api.configs.postgres import get_db_session
from cdn_api.configs.rabbitmq import get_rabbitmq_channel
from cdn_api.configs.settings import get_settings
from cdn_api.main import app
from cdn_api.models.common import BaseModel

import pytest_asyncio

from aio_pika import Channel, connect_robust
from httpx import AsyncClient
from miniopy_async import Minio  # type: ignore
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


settings = get_settings()

GetRequestType = Callable[
    [str, dict[str, Any]],
    Awaitable[tuple[dict, int]],
]


@pytest_asyncio.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def postgres_engine():
    engine = create_async_engine(
        settings.postgres_dsn(),
        echo=False,
        future=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
        await conn.run_sync(BaseModel.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session(postgres_engine: Engine):
    async_session = cast(
        sessionmaker,
        sessionmaker(
            cast(Engine, postgres_engine),
            class_=AsyncSession,
            expire_on_commit=False,
        ),
    )

    async def override_get_db() -> AsyncGenerator[None, AsyncSession]:
        async with async_session() as db:
            yield db

    app.dependency_overrides[get_db_session] = override_get_db

    async with async_session() as db:
        yield db


@pytest_asyncio.fixture(scope="function")
async def minio_client():
    client = Minio(
        endpoint=settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=False,
    )

    async def override_get_minio_client() -> Minio:
        return client

    app.dependency_overrides[get_s3_client] = override_get_minio_client

    yield client

    for bucket in await client.list_buckets():
        for obj in await client.list_objects(bucket):
            client.remove_object(bucket, obj.object_name)
        await client.remove_bucket(bucket)


connection = None


@pytest_asyncio.fixture(scope="function")
async def rabbitmq_channel():
    global connection
    connection = await connect_robust(settings.rabbitmq_dsn())

    async def override_get_rabbitmq_channel() -> AsyncGenerator[None, Channel]:
        return await connection.channel(publisher_confirms=False)

    app.dependency_overrides[
        get_rabbitmq_channel
    ] = override_get_rabbitmq_channel

    yield connection.channel(publisher_confirms=False)

    await connection.close()


@pytest_asyncio.fixture(scope="function")
async def api_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

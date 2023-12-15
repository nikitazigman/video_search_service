from collections.abc import Awaitable, Callable
from typing import Any, cast

import pytest_asyncio  # type: ignore
from faststream.rabbit import TestRabbitBroker
from miniopy_async import Minio  # type: ignore
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from video_converter.configs.minio import init_s3_client
from video_converter.configs.postgres import init_async_engine
from video_converter.configs.settings import get_settings
from video_converter.main import broker
from video_converter.models.common import BaseModel

settings = get_settings()

GetRequestType = Callable[
    [str, dict[str, Any]],
    Awaitable[tuple[dict, int]],
]


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

    yield client

    for bucket in await client.list_buckets():
        for obj in await client.list_objects(bucket):
            client.remove_object(bucket, obj.object_name)
        await client.remove_bucket(bucket)


@pytest_asyncio.fixture(scope="function")
async def rabbitmq_channel():
    init_s3_client(settings=settings)
    await init_async_engine(settings=settings)
    async with TestRabbitBroker(broker) as test_broker:
        yield test_broker

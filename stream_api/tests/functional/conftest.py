import typing as tp

import httpx
import psycopg
import psycopg.rows
import psycopg.sql
import pytest_asyncio

from stream_api.dependencies import databases
from stream_api.main import app
from stream_api.settings.app import get_app_settings
from tests.functional import utils


settings = get_app_settings()


@pytest_asyncio.fixture(scope="function")
async def db_connection() -> tp.AsyncGenerator[psycopg.AsyncConnection, None]:
    _conn = await psycopg.AsyncConnection.connect(
        conninfo=settings.postgres.dsn,
        autocommit=True,
        row_factory=psycopg.rows.dict_row,
    )
    await utils.truncate_db_tables(cursor=_conn.cursor())

    async def override_get_db_conn() -> (
        tp.AsyncGenerator[psycopg.AsyncConnection, None]
    ):
        async with _conn:
            yield _conn

    app.dependency_overrides[databases.get_db_connection] = override_get_db_conn

    async with _conn:
        yield _conn

    if not _conn.closed:
        await _conn.close()


@pytest_asyncio.fixture(scope="function")
async def http_client():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client

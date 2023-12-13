import typing as tp

import psycopg
import psycopg.rows
import psycopg_pool

from stream_api.settings.app import AppSettings


_conn_pool: psycopg_pool.AsyncConnectionPool | None = None


async def open_db_connection_pool(settings: AppSettings) -> None:
    global _conn_pool  # noqa: PLW0603

    _conn_pool = psycopg_pool.AsyncConnectionPool(
        conninfo=settings.postgres.dsn,
        kwargs={"autocommit": False, "row_factory": psycopg.rows.dict_row},
    )
    await _conn_pool.open()


async def close_db_connection_pool() -> None:
    if _conn_pool is not None and not _conn_pool.closed:
        await _conn_pool.close()


async def get_db_connection() -> tp.AsyncGenerator[psycopg.AsyncConnection, None]:
    if _conn_pool is None:
        raise RuntimeError("DB connection pool has not been defined.")

    async with _conn_pool.connection() as conn:
        yield conn

import typing as tp

import psycopg
import psycopg.rows

from stream_api.settings.app import AppSettings


_conn: psycopg.AsyncConnection | None = None


async def init_db_connection(settings: AppSettings) -> None:
    _conn = await psycopg.AsyncConnection.connect(
        conninfo=settings.postgres.dsn,
        row_factory=psycopg.rows.dict_row,
    )


async def close_db_connection() -> None:
    if _conn is None:
        raise RuntimeError("DB connection has not been defined.")

    if not _conn.closed:
        await _conn.close()


async def get_db_connection() -> tp.AsyncGenerator[psycopg.AsyncConnection, None]:
    if _conn is None:
        raise RuntimeError("DB connection has not been defined.")

    async with _conn:
        yield _conn

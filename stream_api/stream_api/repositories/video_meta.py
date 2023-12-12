import typing as tp
import uuid

import psycopg
import psycopg.sql

from stream_api import schemas


class VideoMetaRepositoryProtocol(tp.Protocol):
    async def get_by_id(self, video_id: uuid.UUID) -> schemas.VideoMeta | None:
        ...


class VideoMetaPostgresRepository:
    def __init__(self, connection: psycopg.AsyncConnection) -> None:
        self.conn = connection

    async def get_by_id(self, video_id: uuid.UUID) -> schemas.VideoMeta | None:
        query = psycopg.sql.SQL(
            "SELECT id, name, bucket_original, bucket_hlc "
            "FROM cdn_api.video_meta WHERE id = %s"
        )
        async with self.conn.cursor() as curs:
            await curs.execute(query=query, params=[str(video_id)])
            result = await curs.fetchone()

        return schemas.VideoMeta(**result) if result else None


async def get_video_meta_repo(
    connection: psycopg.AsyncConnection,
) -> VideoMetaRepositoryProtocol:
    return VideoMetaPostgresRepository(connection=connection)

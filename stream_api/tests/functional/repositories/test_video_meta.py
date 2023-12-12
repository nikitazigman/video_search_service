import datetime
import uuid

import psycopg
import psycopg.sql
import pytest

from stream_api import repositories as repos
from stream_api import schemas as schemas


pytestmark = pytest.mark.asyncio


class TestVideoMetaPostgresRepository:
    repo_cls = repos.VideoMetaPostgresRepository

    async def test_get_by_id_expected_exists(
        self, db_connection: psycopg.AsyncConnection
    ) -> None:
        expected_schema = schemas.VideoMeta(
            id=uuid.UUID("c1efb7fe-d8a1-45ee-b939-e7c4df8cd666"),
            name="test.mp4",
            bucket_original="original",
            bucket_hlc="processed",
        )

        # Arrange
        query = psycopg.sql.SQL(
            "INSERT INTO {schema}.{table}({fields}) VALUES (%s, %s, %s, %s, %s, %s)"
        ).format(
            fields=psycopg.sql.SQL(",").join(
                [
                    psycopg.sql.Identifier("id"),
                    psycopg.sql.Identifier("name"),
                    psycopg.sql.Identifier("bucket_original"),
                    psycopg.sql.Identifier("bucket_hlc"),
                    psycopg.sql.Identifier("created_at"),
                    psycopg.sql.Identifier("updated_at"),
                ]
            ),
            schema=psycopg.sql.Identifier("cdn_api"),
            table=psycopg.sql.Identifier("video_meta"),
        )
        id_ = uuid.UUID("c1efb7fe-d8a1-45ee-b939-e7c4df8cd666")
        now = datetime.datetime.now(tz=datetime.UTC)

        async with db_connection.cursor() as curs:
            await curs.execute(
                query,
                params=[
                    expected_schema.id,
                    expected_schema.name,
                    expected_schema.bucket_original,
                    expected_schema.bucket_hlc,
                    now,
                    now,
                ],
            )

        # Act
        video_meta = await self.repo_cls(db_connection).get_by_id(video_id=id_)

        # Assert
        assert video_meta == expected_schema

    async def test_get_by_id_expected_does_not_exist(
        self, db_connection: psycopg.AsyncConnection
    ) -> None:
        # Arrange
        id_ = uuid.uuid4()

        # Act
        video_meta = await self.repo_cls(db_connection).get_by_id(video_id=id_)

        # Assert
        assert video_meta is None

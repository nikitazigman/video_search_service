from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from cdn_api.exceptions import DBClientException, DBServerException
from cdn_api.models.video import VideoMeta
from cdn_api.schemas.responses import VideoSchema

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import ValidationError
from sqlalchemy import delete, insert, select
from sqlalchemy.exc import ArgumentError, IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class VideoMetaRepositoryProtocol(Protocol):
    async def get_by_id(self, video_id: UUID) -> VideoSchema:
        ...

    async def get_all_info(self) -> Page[VideoSchema]:
        ...

    async def insert(
        self, name: str, original_bucket: str, bucket_hlc: str, video_id: UUID
    ) -> VideoSchema:
        ...

    async def delete(self, video_id: UUID) -> None:
        ...


class VideoMetaRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, video_id: UUID) -> VideoSchema:
        select_stmt = select(VideoMeta).where(VideoMeta.id == video_id)
        video_meta_model = await self.session.scalar(select_stmt)
        return VideoSchema.model_validate(video_meta_model)

    def _transformer(self, models: Sequence[VideoMeta]) -> list[VideoSchema]:
        return [VideoSchema.model_validate(model) for model in models]

    async def get_all_info(self) -> Page[VideoSchema]:
        files_info = await paginate(
            self.session,
            select(VideoMeta),
            Params(),
            transformer=self._transformer,
        )
        return files_info

    async def insert(
        self, name: str, original_bucket: str, bucket_hlc: str, video_id: UUID
    ) -> VideoSchema:
        try:
            insert_stmt = (
                insert(VideoMeta)
                .values(
                    name=name,
                    bucket_original=original_bucket,
                    bucket_hlc=bucket_hlc,
                    video_id=video_id,
                )
                .returning(VideoMeta)
            )
            video_meta_model = await self.session.scalar(insert_stmt)
            return VideoSchema.model_validate(video_meta_model)
        except (IntegrityError, ValidationError, ArgumentError) as e:
            raise DBClientException("Incorrect data was provided!") from e
        # Any other sql alchemy or network errors should be considered as server failure
        except (OSError, SQLAlchemyError) as e:
            raise DBServerException from e

    async def delete(self, video_id: UUID) -> None:
        delete_stmt = delete(VideoMeta).where(VideoMeta.id == video_id)
        await self.session.execute(delete_stmt)


def get_video_meta_repo(session: AsyncSession) -> VideoMetaRepositoryProtocol:
    return VideoMetaRepository(session)

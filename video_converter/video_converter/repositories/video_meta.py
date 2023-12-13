from typing import Protocol
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from video_converter.models.video import VideoMeta
from video_converter.schemas.video import VideoSchema
from video_converter.exceptions import VideoConverterDBError


class VideoMetaRepositoryProtocol(Protocol):
    async def update(
        self,
        video_id: UUID,
        name: str,
        bucket: str,
    ) -> VideoSchema:
        ...


class VideoMetaRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def update(
        self,
        video_id: UUID,
        name: str,
        bucket: str,
    ) -> VideoSchema:
        try:
            update_stmt = (
                update(VideoMeta)
                .where(VideoMeta.id == video_id)
                .values(name=name, bucket=bucket)
                .returning(VideoMeta),
            )
            video_model = await self.session.scalar(update_stmt)
            return VideoSchema.model_validate(video_model)
        except (SQLAlchemyError, IOError) as e:
            raise VideoConverterDBError from e


def get_video_meta_repo(session: AsyncSession) -> VideoMetaRepositoryProtocol:
    return VideoMetaRepository(session)

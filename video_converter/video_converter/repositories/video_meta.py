from typing import Protocol
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from video_converter.models.video import VideoMeta
from video_converter.schemas.video import VideoSchema


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
        update_stmt = (
            update(VideoMeta)
            .where(VideoMeta.id == video_id)
            .values(name=name, bucket=bucket)
            .returning(VideoMeta),
        )
        video_model = await self.session.scalar(update_stmt)
        return VideoSchema.model_validate(video_model)


def get_video_meta_repo(session: AsyncSession) -> VideoMetaRepositoryProtocol:
    return VideoMetaRepository(session)

from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from cdn_api.models.video import VideoMeta
from cdn_api.schemas.responses import VideoSchema

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class VideoMetaRepositoryProtocol(Protocol):
    async def get_all_info(self) -> Page[VideoSchema]:
        ...

    async def insert(self, name: str, bucket: str) -> VideoSchema:
        ...

    # TODO: implement
    async def delete(self, video_id: UUID) -> None:
        ...


class VideoMetaRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        select, update, delete, insert

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

    async def insert(self, name: str, bucket: str) -> VideoSchema:
        insert_stmt = (
            insert(VideoMeta)
            .values(name=name, bucket=bucket)
            .returning(VideoMeta)
        )
        video_meta_model = await self.session.scalar(insert_stmt)
        return VideoSchema.model_validate(video_meta_model)

    # TODO: implement
    async def delete(self, video_id: UUID) -> None:
        ...


def get_video_meta_repo(session: AsyncSession) -> VideoMetaRepositoryProtocol:
    return VideoMetaRepository(session)

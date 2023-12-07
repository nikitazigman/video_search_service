from types import TracebackType
from typing import Protocol, Self

from cdn_api.repositories.s3 import S3RepoProtocol, get_s3_repo
from cdn_api.repositories.tasks import TaskRepositoryProtocol, get_task_repo
from cdn_api.repositories.video_meta import (
    VideoMetaRepositoryProtocol,
    get_video_meta_repo,
)
from cdn_api.utils.dependencies import DBSessionType, S3ClientType

from miniopy_async import Minio  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession


class VideoUOWProtocol(Protocol):
    s3_repo: S3RepoProtocol
    video_meta_repo: VideoMetaRepositoryProtocol
    task_repo: TaskRepositoryProtocol

    async def __aenter__(self) -> Self:
        ...

    async def __aexit__(
        self,
        exc_type: type[Exception],
        exception: Exception,
        traceback: TracebackType,
    ) -> None:
        ...

    async def commit(self) -> None:
        ...

    async def rollback(self) -> None:
        ...


class FileUOW:
    def __init__(self, sql_session: AsyncSession, s3_client: Minio):
        self.sql_session = sql_session

        self.video_meta_repo = get_video_meta_repo(self.sql_session)
        self.task_repo = get_task_repo(self.sql_session)
        self.s3_repo = get_s3_repo(s3_client)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[Exception],
        exception: Exception,
        traceback: TracebackType,
    ) -> None:
        if exception is not None:
            await self.rollback()
            raise exception

    async def commit(self) -> None:
        await self.sql_session.commit()

    async def rollback(self) -> None:
        await self.sql_session.rollback()


def get_file_uow(
    sql_session: DBSessionType, s3_client: S3ClientType
) -> VideoUOWProtocol:
    return FileUOW(sql_session=sql_session, s3_client=s3_client)

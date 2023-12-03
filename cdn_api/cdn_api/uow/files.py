from types import TracebackType
from typing import Protocol, Self

from cdn_api.repositories.files import (
    ZipRepositoryProtocol,
    get_zip_repository_type,
)
from cdn_api.repositories.files_info import (
    FileInfoRepositoryProtocol,
    get_file_info_repo,
)

from sqlalchemy.ext.asyncio import AsyncSession


class FileUOWProtocol(Protocol):
    zip_repo_cls: type[ZipRepositoryProtocol]
    file_info_repo: FileInfoRepositoryProtocol

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
    def __init__(self, sql_session: AsyncSession):
        self.sql_session = sql_session
        self.zip_repo_cls = get_zip_repository_type()
        self.file_info_repo = get_file_info_repo(self.sql_session)

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
        ...
        # await self.sql_session.commit()

    async def rollback(self) -> None:
        ...
        # await self.sql_session.rollback()


def get_file_uow(sql_session=None) -> FileUOWProtocol:
    return FileUOW(sql_session)

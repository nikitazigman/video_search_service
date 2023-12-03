from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from cdn_api.models.files import File
from cdn_api.schemas.file_info_repo import InsertFileSchema
from cdn_api.schemas.responses import FileSchema

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class FileInfoRepositoryProtocol(Protocol):
    async def get_all_info(self) -> Page[FileSchema]:
        ...

    async def insert_batch(self, files: list[InsertFileSchema]) -> None:
        ...

    async def update(self, hash: str) -> FileSchema:
        ...

    async def delete(self, file_id: UUID) -> None:
        ...


class FileInfoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        select, update, delete, insert

    def _transformer(self, models: Sequence[File]) -> list[FileSchema]:
        return [FileSchema.model_validate(model) for model in models]

    async def get_all_info(self) -> Page[FileSchema]:
        files_info = await paginate(
            self.session,
            select(File),
            Params(),
            transformer=self._transformer,
        )
        return files_info

    async def insert_batch(self, files: list[InsertFileSchema]) -> None:
        insert_stmt = insert(File).values(
            [file.model_dump() for file in files]
        )
        await self.session.execute(insert_stmt)

    async def update(self, hash: str) -> FileSchema:
        ...

    async def delete(self, file_id: UUID) -> None:
        ...


def get_file_info_repo(session: AsyncSession) -> FileInfoRepositoryProtocol:
    return FileInfoRepository(session)

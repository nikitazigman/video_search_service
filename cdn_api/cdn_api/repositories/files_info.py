from datetime import datetime
from typing import Protocol
from uuid import UUID

from cdn_api.schemas.file_info_repo import InsertFileSchema
from cdn_api.schemas.responses import FileSchema

from sqlalchemy.ext.asyncio import AsyncSession


SQL_STORAGE: list[FileSchema] = []


class FileInfoRepositoryProtocol(Protocol):
    async def get_all_info(self) -> list[FileSchema]:
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

    async def get_all_info(self) -> list[FileSchema]:
        return SQL_STORAGE

    async def insert_batch(self, files: list[InsertFileSchema]) -> None:
        schemas = [
            FileSchema(
                id=UUID("f4d1b5e5-3c9e-4f4c-9b5e-5e3c9e4f4c9b"),
                version=1,
                name=file.name,
                path=str(file.path),
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            for file in files
        ]
        SQL_STORAGE.extend(schemas)

    async def update(self, hash: str) -> FileSchema:
        return SQL_STORAGE[0]

    async def delete(self, file_id: UUID) -> None:
        SQL_STORAGE.pop()


def get_file_info_repo(session: AsyncSession) -> FileInfoRepositoryProtocol:
    return FileInfoRepository(session)

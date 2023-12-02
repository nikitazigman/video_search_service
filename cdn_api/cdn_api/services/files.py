from datetime import datetime
from typing import Protocol
from uuid import UUID, uuid4

from cdn_api.schemas.requests import UploadZipArchive
from cdn_api.schemas.responses import FileSchema

from fastapi_pagination import Page, Params


class UploaderProtocol(Protocol):
    def upload(self, zip_archive_stream: UploadZipArchive) -> Page[FileSchema]:
        ...


class RemoverProtocol(Protocol):
    def remove(self, file_id: UUID) -> None:
        ...


class FileService:
    def remove(self, file_id: UUID) -> None:
        return None

    def upload(self, zip_archive_stream: UploadZipArchive) -> Page[FileSchema]:
        fake_response = [
            FileSchema(
                id=uuid4(),
                name=f"file_{i}.txt",
                path=f"path/to/file_{i}.txt",
                version=1,
                hash_code=str(hash(i)),
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            for i in range(10)
        ]

        return Page.create(
            items=fake_response, params=Params(), total=len(fake_response)
        )


def get_uploader() -> UploaderProtocol:
    return FileService()


def get_remover() -> RemoverProtocol:
    return FileService()

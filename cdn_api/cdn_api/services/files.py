import zipfile

from datetime import datetime
from pathlib import Path
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
    def insert_files_to_sql(
        self, files: list[zipfile.ZipInfo], path_to_store: Path
    ) -> Page[FileSchema]:
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

    def remove(self, file_id: UUID) -> None:
        return None

    def upload(self, zip_archive_stream: UploadZipArchive) -> Page[FileSchema]:
        archive = zip_archive_stream.zip_archive.file
        path_to_store = Path(zip_archive_stream.path)

        # uow
        with zipfile.ZipFile(archive) as zip:
            info_list = zip.infolist()
            files_page = self.insert_files_to_sql(info_list, path_to_store)
            zip.extractall(path_to_store)

        return files_page


def get_uploader() -> UploaderProtocol:
    return FileService()


def get_remover() -> RemoverProtocol:
    return FileService()

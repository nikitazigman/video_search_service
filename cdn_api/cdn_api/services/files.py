from pathlib import Path
from typing import Annotated, Protocol
from uuid import UUID

from cdn_api.schemas.requests import UploadZipArchive
from cdn_api.schemas.responses import FileSchema
from cdn_api.uow.files import FileUOWProtocol, get_file_uow
from cdn_api.utils import utils

from fastapi import Depends


class UploaderProtocol(Protocol):
    async def upload(
        self, zip_archive_stream: UploadZipArchive
    ) -> list[FileSchema]:
        ...


class RemoverProtocol(Protocol):
    async def remove(self, file_id: UUID) -> None:
        ...


class FileService:
    def __init__(self, uow: FileUOWProtocol) -> None:
        self.uow = uow

    async def remove(self, file_id: UUID) -> None:
        return None

    async def upload(
        self, zip_archive_stream: UploadZipArchive
    ) -> list[FileSchema]:
        archive = zip_archive_stream.zip_archive.file
        path_to_store = Path(zip_archive_stream.path)

        async with self.uow as uow:
            async with uow.zip_repo_cls(archive) as zip:
                info_list = await zip.get_info()
                insert_data = utils.transform_zip_info_to_insert_file(
                    info_list, path_to_store
                )
                await uow.file_info_repo.insert_batch(insert_data)
                await zip.extract(path=path_to_store, members=info_list)

                files_page = await uow.file_info_repo.get_all_info()
                await uow.commit()

        return files_page


FileRepositoryType = Annotated[FileUOWProtocol, Depends(get_file_uow)]


def get_uploader(uow: FileRepositoryType) -> UploaderProtocol:
    return FileService(uow)


def get_remover(uow: FileRepositoryType) -> RemoverProtocol:
    return FileService(uow)

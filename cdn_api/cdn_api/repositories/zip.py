from pathlib import Path
from types import TracebackType
from typing import BinaryIO, Protocol, Self
from zipfile import ZipFile, ZipInfo

from asgiref.sync import sync_to_async


class ZipRepositoryProtocol(Protocol):
    def __init__(self, archive: BinaryIO) -> None:
        ...

    async def __aenter__(self) -> Self:
        ...

    async def __aexit__(
        self,
        exc_type: type[Exception],
        exception: Exception,
        traceback: TracebackType,
    ) -> None:
        ...

    async def get_info(self) -> list[ZipInfo]:
        ...

    async def extract(self, path: Path, members: list[ZipInfo]) -> None:
        ...


class ZipRepository:
    def __init__(self, archive: BinaryIO) -> None:
        self.archive = archive
        self.zip: ZipFile | None = None

    @sync_to_async
    def _open(self) -> ZipFile:
        return ZipFile(self.archive)

    async def __aenter__(self) -> Self:
        self.zip = await self._open()

        return self

    async def __aexit__(
        self,
        exc_type: type[Exception],
        exception: Exception,
        traceback: TracebackType,
    ) -> None:
        if self.zip is not None:
            self.zip.close()

    @sync_to_async
    def get_info(self) -> list[ZipInfo]:
        if self.zip is None:
            raise ValueError("Zip file is not initialized.")
        files_info = [
            zip_info
            for zip_info in self.zip.infolist()
            if not zip_info.is_dir() and not zip_info.filename.startswith("__")
        ]
        return files_info

    @sync_to_async
    def extract(self, path: Path, members: list[ZipInfo]) -> None:
        if self.zip is None:
            raise ValueError("Zip file is not initialized.")

        self.zip.extractall(path, members=members)


def get_zip_repository_type() -> type[ZipRepositoryProtocol]:
    return ZipRepository

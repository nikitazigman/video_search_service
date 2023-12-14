from pathlib import Path
from typing import Protocol

from miniopy_async import Minio  # type: ignore
from miniopy_async.error import MinioException

from video_converter.exceptions import VideoConverterMinioException


class S3RepoProtocol(Protocol):
    async def upload_chunks(self, bucket_name: str, folder: Path) -> None:
        """
        Upload videos to s3 bucket.
        """

    async def download_video(
        self, bucket_name: str, file_name: str, path: Path
    ) -> Path:
        """
        Download video from s3 bucket.
        """


class S3Repo:
    def __init__(self, client: Minio):
        self.client = client

    async def upload_file(
        self, file: Path, bucket_name: str, relative_path: Path
    ) -> None:
        try:
            await self.client.fput_object(
                bucket_name=bucket_name,
                object_name=str(file.relative_to(relative_path)),
                file_path=str(file),
            )
        except (OSError, MinioException) as e:
            raise VideoConverterMinioException from e

    async def create_bucket(self, bucket_name: str) -> None:
        try:
            if await self.client.bucket_exists(bucket_name):
                return None

            await self.client.make_bucket(bucket_name)
        except(OSError, MinioException) as e:
            raise VideoConverterMinioException from e

    async def upload_chunks(self, bucket_name: str, folder: Path) -> None:
        await self.create_bucket(bucket_name)
        relative_path = folder.parent

        async def _upload_files(original_folder: Path) -> None:
            for item in original_folder.iterdir():
                if item.is_dir():
                    await _upload_files(item)
                else:
                    await self.upload_file(item, bucket_name, relative_path)

        try:
            await _upload_files(folder)
        except(OSError, MinioException) as e:
            raise VideoConverterMinioException from e

    async def download_video(
        self, bucket_name: str, file_name: str, path: Path
    ) -> Path:
        try:
            await self.client.fget_object(
                bucket_name=bucket_name,
                object_name=file_name,
                file_path=str(path),
            )
            return path / file_name
        except (OSError, MinioException) as e:
            raise VideoConverterMinioException from e


def get_s3_repo(s3_client: Minio) -> S3RepoProtocol:
    return S3Repo(s3_client)

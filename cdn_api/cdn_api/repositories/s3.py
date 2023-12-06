from pathlib import Path
from typing import Protocol

from minio import Minio  # type: ignore


class S3RepoProtocol(Protocol):
    async def upload_files(
        self,
        bucket_name: str,
        path_to_folder: Path,
    ) -> None:
        """
        Upload files to s3 bucket.

        Args:
            bucket_name: bucket name
            path_to_folder: path to folder with files
        """


class S3Repo:
    CHUCK_SIZE_BYTES = 1024 * 1024 * 5  # 5MB

    def __init__(self, client: Minio):
        self.client = client

    async def upload_file(
        self, bucket: str, file: Path, relative_path: Path
    ) -> None:
        self.client.fput_object(
            bucket_name=bucket,
            object_name=str(file.relative_to(relative_path)),
            file_path=str(file),
        )

    async def upload_files(
        self,
        bucket_name: str,
        path_to_folder: Path,
    ) -> None:
        relative_path = path_to_folder
        bucket = self.client.bucket_exists(str(bucket_name))
        if not bucket:
            self.client.make_bucket(bucket_name)

        async def _upload_files(path_to_folder: Path):
            for item in path_to_folder.iterdir():
                if item.is_file():
                    await self.upload_file(bucket_name, item, relative_path)
                else:
                    await _upload_files(path_to_folder=item)

        await _upload_files(path_to_folder)


def get_s3_repo(s3_client: Minio) -> S3RepoProtocol:
    return S3Repo(s3_client)

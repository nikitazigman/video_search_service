from typing import Protocol

from fastapi import UploadFile
from miniopy_async import Minio  # type: ignore


class S3RepoProtocol(Protocol):
    async def upload_video(
        self, bucket_name: str, file_name: str, file: UploadFile
    ) -> None:
        """
        Upload video to s3 bucket.
        """

    async def create_bucket(self, bucket_name: str) -> None:
        """
        Create bucket in s3.
        """

    async def delete_bucket(self, bucket_name: str) -> None:
        """
        Delete bucket in s3.
        """

    async def delete_file(self, bucket_name: str, file_name: str) -> None:
        """
        Delete file in s3.
        """


class S3Repo:
    def __init__(self, client: Minio):
        self.client = client

    async def create_bucket(self, bucket_name: str) -> None:
        if await self.client.bucket_exists(bucket_name):
            return None

        await self.client.make_bucket(bucket_name)

    async def delete_bucket(self, bucket_name: str) -> None:
        await self.client.remove_objects(bucket_name, recursive=True)
        await self.client.remove_bucket(bucket_name)

    async def delete_file(self, bucket_name: str, file_name: str) -> None:
        await self.client.remove_object(bucket_name, file_name)

    async def upload_video(
        self, bucket_name: str, file_name: str, file: UploadFile
    ) -> None:
        await self.create_bucket(bucket_name)

        await self.client.put_object(
            bucket_name=bucket_name,
            object_name=file_name,
            data=file.file,
            length=file.size,
        )


def get_s3_repo(s3_client: Minio) -> S3RepoProtocol:
    return S3Repo(s3_client)

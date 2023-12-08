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


class S3Repo:
    def __init__(self, client: Minio):
        self.client = client

    async def upload_video(
        self, bucket_name: str, file_name: str, file: UploadFile
    ) -> None:
        bucket = await self.client.bucket_exists(bucket_name)
        if not bucket:
            await self.client.make_bucket(bucket_name)

        await self.client.put_object(
            bucket_name=bucket_name,
            object_name=file_name,
            data=file.file,
            length=file.size,
            content_type="mp4",
        )


def get_s3_repo(s3_client: Minio) -> S3RepoProtocol:
    return S3Repo(s3_client)

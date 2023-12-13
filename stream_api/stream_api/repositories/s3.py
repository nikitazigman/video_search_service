import datetime
import pathlib
import typing as tp

import fastapi
import miniopy_async
import miniopy_async.datatypes
import miniopy_async.error
import structlog

from stream_api.dependencies import s3
from stream_api.repositories.exceptions import (
    S3BucketDoesNotExistError,
    S3RepositoryError,
)


logger = structlog.get_logger()


class S3RepositoryProtocol(tp.Protocol):
    async def list_objects(
        self, bucket_name: str, dir_name: str
    ) -> list[miniopy_async.datatypes.Object]:
        ...

    async def get_presigned_url(
        self,
        bucket_name: str,
        s3_object: miniopy_async.datatypes.Object,
        expires_in_secs: int,
        method: str,
    ) -> str:
        ...

    async def download_file(
        self, bucket_name: str, object_name: str, target_filepath: pathlib.Path
    ) -> pathlib.Path:
        ...

    async def validate_bucket_exists(self, bucket_name: str) -> None:
        ...


class S3MinioRepository:
    def __init__(self, client: miniopy_async.Minio) -> None:
        self.client = client

    async def list_objects(
        self, bucket_name: str, dir_name: str
    ) -> list[miniopy_async.datatypes.Object]:
        try:
            return await self.client.list_objects(
                bucket_name=bucket_name, prefix=dir_name, recursive=True
            )
        except (OSError, miniopy_async.error.MinioException) as err:
            raise S3RepositoryError from err

    async def get_presigned_url(
        self,
        bucket_name: str,
        s3_object: miniopy_async.datatypes.Object,
        expires_in_secs: int,
        method: str = "GET",
    ) -> str:
        try:
            return await self.client.get_presigned_url(
                method=method,
                bucket_name=bucket_name,
                object_name=s3_object.object_name,
                expires=datetime.timedelta(seconds=expires_in_secs),
            )
        except (OSError, miniopy_async.error.MinioException) as err:
            raise S3RepositoryError from err

    async def download_file(
        self,
        bucket_name: str,
        object_name: str,
        target_filepath: pathlib.Path,
    ) -> pathlib.Path:
        await logger.debug(
            "Download file from s3 to the target filepath",
            bucket_name=bucket_name,
            object_name=object_name,
            target_filepath=target_filepath,
        )
        try:
            await self.client.fget_object(
                bucket_name=bucket_name,
                object_name=object_name,
                file_path=str(target_filepath),
            )
        except (OSError, miniopy_async.error.MinioException) as err:
            raise S3RepositoryError from err

        return target_filepath

    async def validate_bucket_exists(self, bucket_name: str) -> None:
        if not await self.client.bucket_exists(bucket_name=bucket_name):
            raise S3BucketDoesNotExistError(
                f"S3 bucket does not exist: '{bucket_name}'."
            )


async def get_s3_repository(
    s3_client: tp.Annotated[miniopy_async.Minio, fastapi.Depends(s3.get_s3_client)],
) -> S3RepositoryProtocol:
    return S3MinioRepository(client=s3_client)

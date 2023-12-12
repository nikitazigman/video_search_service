import miniopy_async

from stream_api.settings.app import AppSettings


_s3_client: miniopy_async.Minio | None = None


async def init_s3_client(settings: AppSettings) -> None:
    _s3_client = miniopy_async.Minio(
        endpoint=settings.minio.dsn,
        access_key=settings.minio.access_key,
        secret_key=settings.minio.secret_key,
        secure=not settings.service.debug,
    )


async def get_s3_client() -> miniopy_async.Minio:
    if _s3_client is None:
        raise RuntimeError("S3 client is not initialized")

    return _s3_client

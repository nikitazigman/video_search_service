from miniopy_async import Minio  # type: ignore

from video_converter.configs.settings import Settings

_s3_client: None | Minio = None


def init_s3_client(settings: Settings) -> None:
    global _s3_client

    _s3_client = Minio(
        endpoint=settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_secure,
    )


def get_s3_client() -> Minio:
    if _s3_client is None:
        raise RuntimeError("S3 client is not initialized")

    return _s3_client

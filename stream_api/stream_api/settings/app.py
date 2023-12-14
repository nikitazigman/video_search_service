import functools

from stream_api.settings.base import BaseAppSettings
from stream_api.settings.integration import IntegrationSettings
from stream_api.settings.logging import LoggingSettings
from stream_api.settings.minio import MinioSettings
from stream_api.settings.postgres import PostgresSettings
from stream_api.settings.service import ServiceSettings


class AppSettings(BaseAppSettings):
    service: ServiceSettings = ServiceSettings()
    logging: LoggingSettings = LoggingSettings()
    postgres: PostgresSettings = PostgresSettings()
    minio: MinioSettings = MinioSettings()
    integration: IntegrationSettings = IntegrationSettings()


@functools.lru_cache(maxsize=1)
def get_app_settings() -> AppSettings:
    return AppSettings()

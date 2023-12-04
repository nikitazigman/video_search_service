from functools import lru_cache

import pydantic

from cdn_worker.settings.base import BaseAppSettings
from cdn_worker.settings.database import PostgresSettings
from cdn_worker.settings.logging import LoggingSettings
from cdn_worker.settings.service import ServiceSettings


class AppSettings(BaseAppSettings):
    debug: bool = pydantic.Field(env="SERVICE_DEBUG", default=False)

    service: ServiceSettings = ServiceSettings()
    logging: LoggingSettings = LoggingSettings()
    postgres: PostgresSettings = PostgresSettings()


@lru_cache(maxsize=1)
def get_app_settings() -> AppSettings:
    return AppSettings()

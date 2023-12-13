from pydantic_settings import SettingsConfigDict

from stream_api.settings.base import BaseAppSettings


class ServiceSettings(BaseAppSettings):
    model_config = SettingsConfigDict(env_prefix="service_")

    name: str
    description: str = "Stream API"
    version: str = "0.1.0"

    host: str
    port: int
    debug: bool = False

    s3_url_expire_in_secs: int = 60 * 60 * 24 * 1  # 1 day

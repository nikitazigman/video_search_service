from pydantic_settings import SettingsConfigDict

from cdn_worker.settings.base import BaseAppSettings


class ServiceSettings(BaseAppSettings):
    model_config = SettingsConfigDict(env_prefix="service_")

    name: str
    debug: bool = False

    description: str = ""
    version: str = "0.1.0"

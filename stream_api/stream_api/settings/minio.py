from pydantic_settings import SettingsConfigDict

from stream_api.settings.base import BaseAppSettings


class MinioSettings(BaseAppSettings):
    model_config = SettingsConfigDict(env_prefix="minio_")

    host: str
    port: int

    access_key: str
    secret_key: str

    @property
    def dsn(self) -> str:
        return f"{self.host}:{self.port}"

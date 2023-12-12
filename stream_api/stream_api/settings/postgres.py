import pydantic

from pydantic_settings import SettingsConfigDict

from stream_api.settings.base import BaseAppSettings


class PostgresSettings(BaseAppSettings):
    model_config = SettingsConfigDict(env_prefix="postgres_")

    db: str
    user: str
    password: str
    host: str
    port: int
    scheme: str = "postgresql"

    @property
    def dsn(self) -> str:
        return str(
            pydantic.PostgresDsn.build(
                scheme=self.scheme,
                username=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                path=self.db,
            ),
        )

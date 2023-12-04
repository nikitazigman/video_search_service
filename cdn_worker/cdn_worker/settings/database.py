import pydantic
import pydantic_settings

from cdn_worker.settings.base import BaseAppSettings


class PostgresSettings(BaseAppSettings):
    model_config = pydantic_settings.SettingsConfigDict(env_prefix="postgres_")

    db: str
    user: str
    password: str
    host: str
    port: int
    db_schema: str

    @property
    def dsn(self) -> str:
        return str(
            pydantic.PostgresDsn.build(
                scheme="postgresql",
                username=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                path=f"{self.db}",
            )
        )

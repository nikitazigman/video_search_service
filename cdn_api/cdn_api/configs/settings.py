from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    postgres_schema: str

    redis_host: str
    redis_port: int

    cache_expire_in_seconds: int

    service_name: str
    service_description: str
    service_host: str
    service_port: int

    debug: bool = False
    logging_level: str = "INFO"

    jwt_encoding_algorithm: str = "HS256"
    jwt_secret_key: str

    rate_limiter_times: int = 10
    rate_limiter_seconds: int = 60

    def postgres_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    def redis_dsn(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}"


@lru_cache(maxsize=1)
def get_settings():
    return Settings()

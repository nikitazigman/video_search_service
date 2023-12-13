from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_DIR = Path(__file__).resolve().parent.parent.parent.joinpath(".env")


class BaseAppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_DIR,
        env_file_encoding="utf-8",
        extra="ignore",
    )

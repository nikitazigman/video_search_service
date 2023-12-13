from pydantic import HttpUrl
from pydantic_settings import SettingsConfigDict

from stream_api.settings.base import BaseAppSettings


class IntegrationSettings(BaseAppSettings):
    model_config = SettingsConfigDict(env_prefix="integration_")

    auth_access_token: str
    auth_jwt_verify_url: HttpUrl

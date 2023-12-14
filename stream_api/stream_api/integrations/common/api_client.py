import typing as tp

import fastapi
import httpx
import orjson
import pydantic
import structlog

from stream_api.integrations.common.exceptions import IntegrationAPIClientError
from stream_api.settings.app import AppSettings, get_app_settings


logger = structlog.get_logger()


class APIClientProtocol(tp.Protocol):
    async def post(self, path: str, body: dict, headers: dict) -> dict:
        ...


class APIClient:
    def __init__(self, base_url: pydantic.HttpUrl, auth_access_token: str) -> None:
        self.base_url = base_url
        self._access_token = auth_access_token

    async def post(self, path: str, body: dict, headers: dict) -> dict:
        url = f"{self.base_url}{path}"

        await logger.debug("Send POST request", url=url)

        headers["Authorization"] = f"Bearer {self._access_token}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url=url, content=orjson.dumps(body), headers=headers
                )

            response.raise_for_status()

        except httpx.HTTPError as err:
            raise IntegrationAPIClientError from err

        return response.json()


async def get_api_client(
    settings: tp.Annotated[AppSettings, fastapi.Depends(get_app_settings)],
) -> APIClientProtocol:
    return APIClient(
        base_url=settings.integration.auth_jwt_verify_url,
        auth_access_token=settings.integration.auth_access_token,
    )

import enum
import typing as tp

import fastapi
import pydantic
import structlog

from stream_api.integrations.common.api_client import APIClientProtocol, get_api_client
from stream_api.integrations.common.exceptions import IntegrationAPIClientError
from stream_api.integrations.schemas import auth as auth_schemas
from stream_api.integrations.services.exceptions import (
    AuthenticationError,
    AuthServiceError,
)


logger = structlog.get_logger()


class Status(enum.StrEnum):
    VALID: str = "valid"
    INVALID: str = "invalid"


class AccessTokenInfo(pydantic.BaseModel):
    status: Status
    detail: str


class AuthServiceProtocol(tp.Protocol):
    async def verify_access_token(self, jwt: auth_schemas.AccessToken) -> None:
        ...


class AuthService:
    def __init__(self, api_client: APIClientProtocol) -> None:
        self._api_client = api_client

    async def verify_access_token(self, jwt: auth_schemas.AccessToken) -> None:
        await logger.debug("Verify JWT")

        try:
            response_data = await self._api_client.post(
                path="",
                body=jwt.model_dump(),
                headers={},
            )

        except IntegrationAPIClientError as err:
            raise AuthServiceError from err

        jwt_info = AccessTokenInfo(**response_data)

        log_event = "JWT verification status"
        if jwt_info.status == Status.INVALID:
            await logger.debug(log_event, status=Status.INVALID)
            raise AuthenticationError

        await logger.debug(log_event, status=Status.VALID)


async def get_auth_service(
    api_client: tp.Annotated[APIClientProtocol, fastapi.Depends(get_api_client)],
) -> AuthServiceProtocol:
    return AuthService(api_client=api_client)

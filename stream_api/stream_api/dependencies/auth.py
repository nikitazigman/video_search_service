import fastapi

from starlette import status

from stream_api.integrations.schemas import auth as auth_schemas
from stream_api.integrations.services.auth import (
    AuthServiceProtocol,
    get_api_client,
    get_auth_service,
)
from stream_api.settings.app import get_app_settings


settings = get_app_settings()


async def verify_access_token(jwt: str):
    auth_service: AuthServiceProtocol = await get_auth_service(
        api_client=await get_api_client(settings=settings)
    )
    await auth_service.verify_access_token(
        jwt=auth_schemas.AccessToken(token_string=jwt)
    )


class JWTBearer(fastapi.security.HTTPBearer):
    def __init__(self, auto_error: bool = True) -> None:
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: fastapi.requests.Request) -> None:
        credentials = await super().__call__(request)
        if not credentials:
            raise fastapi.HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code.",
            )

        if credentials.scheme != "Bearer":
            raise fastapi.HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Bearer token might be accepted.",
            )

        await verify_access_token(credentials.credentials)

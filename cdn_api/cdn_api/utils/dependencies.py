import http

from collections.abc import Callable, Coroutine
from typing import Annotated

from cdn_api.configs.minio import get_s3_client
from cdn_api.configs.postgres import get_db_session
from cdn_api.configs.redis import get_redis_client
from cdn_api.configs.settings import get_settings
from cdn_api.schemas.jwt import JwtClaims
from cdn_api.utils.authorization import JWTBearer

from fastapi import Depends, HTTPException
from fastapi_limiter.depends import RateLimiter  # type: ignore
from fastapi_pagination import Params
from miniopy_async import Minio  # type: ignore
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession


settings = get_settings()

S3ClientType = Annotated[Minio, Depends(get_s3_client)]
DBSessionType = Annotated[AsyncSession, Depends(get_db_session)]
RedisClientType = Annotated[Redis, Depends(get_redis_client)]
PaginationParamsType = Annotated[Params, Depends()]
UserTokenType = Annotated[JwtClaims, Depends(JWTBearer())]
RateLimiterType = Annotated[
    RateLimiter,
    Depends(
        RateLimiter(
            times=settings.rate_limiter_times,
            seconds=settings.rate_limiter_seconds,
        )
    ),
]

CheckPermissionType = Callable[
    [UserTokenType],
    Coroutine[None, None, JwtClaims],
]


def check_permission(user_role: str) -> CheckPermissionType:
    async def _check_permission(user_token: UserTokenType) -> JwtClaims:
        if user_role != user_token.user.role:
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN,
                detail=(
                    "User does not have a permission"
                    " to perform this action."
                ),
            )

        return user_token

    return _check_permission

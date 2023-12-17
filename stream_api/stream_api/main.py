import logging.config
import typing as tp

from contextlib import asynccontextmanager

import fastapi.responses
import structlog
import uvicorn

from starlette import status

from stream_api.api.v1.manifest import router as hls_manifest_router
from stream_api.core.exceptions import ServiceError
from stream_api.dependencies import databases, s3
from stream_api.settings.app import get_app_settings
from stream_api.settings.logging import configure_logger


settings = get_app_settings()

logging.config.dictConfig(settings.logging.config)
configure_logger(enable_async_logger=True)
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI) -> tp.AsyncGenerator[None, None]:
    await databases.open_db_connection_pool(settings=settings)
    await s3.init_s3_client(settings=settings)

    yield

    await databases.close_db_connection_pool()


app = fastapi.FastAPI(
    lifespan=lifespan,
    title=settings.service.name,
    description=settings.service.description,
    docs_url="/docs",
    openapi_url="/docs/openapi.json",
    version=settings.service.version,
    debug=settings.service.debug,
    default_response_class=fastapi.responses.ORJSONResponse,
)

app.include_router(hls_manifest_router, prefix="/api/v1", tags=["hls"])


@app.get("/ping")
async def pong() -> dict[str, str]:
    await logger.info("ping")
    return {"ping": "pong!"}


@app.exception_handler(ServiceError)
async def service_error_handler(
    request: fastapi.requests.Request, exc: ServiceError
) -> fastapi.responses.ORJSONResponse:
    await logger.exception(exc)
    return fastapi.responses.ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"{settings.service.name} internal error"},
    )


if __name__ == "__main__":
    uvicorn.run(
        "stream_api.main:app",
        host=settings.service.host,
        port=settings.service.port,
        reload=settings.service.debug,
    )

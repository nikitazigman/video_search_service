import logging.config
import typing as tp

from contextlib import asynccontextmanager

import fastapi.responses
import structlog
import uvicorn

from stream_api.dependencies import databases, s3
from stream_api.settings.app import get_app_settings
from stream_api.settings.logging import configure_logger


settings = get_app_settings()

logging.config.dictConfig(settings.logging.config)
configure_logger(enable_async_logger=True)
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI) -> tp.AsyncGenerator[None, None]:  # noqa: ARG001
    await databases.init_db_connection(settings=settings)
    await s3.init_s3_client(settings=settings)

    yield

    await databases.close_db_connection()


app = fastapi.FastAPI(
    lifespan=lifespan,
    title=settings.service.name,
    description=settings.service.description,
    docs_url="/docs",
    openapi_url="/api/openapi.json",
    version=settings.service.version,
    debug=settings.service.debug,
    default_response_class=fastapi.responses.ORJSONResponse,
)


@app.get("/ping")
async def pong() -> dict[str, str]:
    await logger.info("ping")
    return {"ping": "pong!"}


if __name__ == "__main__":
    uvicorn.run(
        "stream_api.main:app",
        host=settings.service.host,
        port=settings.service.port,
        reload=settings.service.debug,
    )

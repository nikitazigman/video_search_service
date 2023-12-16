import logging

from contextlib import asynccontextmanager

from cdn_api.api.v1.video import router as files_router
from cdn_api.api.v1.task import router as task_router
from cdn_api.configs.minio import init_s3_client
from cdn_api.configs.postgres import close_async_engine, init_async_engine
from cdn_api.configs.rabbitmq import close_rabbitmq, init_rabbitmq
from cdn_api.configs.settings import get_settings

import uvicorn

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse


settings = get_settings()

logging.config.dictConfig(settings.logging_config)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_async_engine(settings)
    await init_rabbitmq(settings)
    init_s3_client(settings)
    yield
    await close_rabbitmq()
    await close_async_engine()


app = FastAPI(
    lifespan=lifespan,
    title=settings.service_name,
    description=settings.service_description,
    docs_url="/docs",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    version="0.1.0",
)


@app.get("/ping")
def pong() -> dict[str, str]:
    return {"ping": "pong!"}


app.include_router(files_router, prefix="/api/v1", tags=["files"])
app.include_router(task_router, prefix="/api/v1/tasks", tags=["tasks"])

if __name__ == "__main__":
    uvicorn.run(
        "cdn_api.main:app",
        host=settings.service_host,
        port=settings.service_port,
        reload=settings.debug,
    )

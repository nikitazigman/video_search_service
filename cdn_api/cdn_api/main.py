from contextlib import asynccontextmanager

from cdn_api.api.v1.files import router as files_router
from cdn_api.configs.settings import get_settings

import uvicorn

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


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


app.include_router(files_router, prefix="/api/v1", tags=["films"])

if __name__ == "__main__":
    uvicorn.run(
        "cdn_api.main:app",
        host=settings.service_host,
        port=settings.service_port,
        reload=settings.debug,
    )

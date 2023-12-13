import typing as tp
import uuid

import fastapi
import fastapi.responses
import starlette.background
import structlog

from starlette import status

from stream_api.dependencies import requests as request_deps
from stream_api.services.manifest import (
    VideoManifestFileServiceProtocol,
    get_video_manifest_service,
)
from stream_api.settings.app import get_app_settings
from stream_api.utils.files import remove_file


settings = get_app_settings()

logger = structlog.get_logger()

router = fastapi.APIRouter()


@router.get(
    path="/hls/manifest/{video_id}",
    summary="Get a video manifest file",
    description="Get a HLS video manifest file (.m3u8) by video file id.",
    status_code=status.HTTP_200_OK,
)
async def get_video_manifest_file(
    video_id: uuid.UUID,
    video_manifest_service: tp.Annotated[
        VideoManifestFileServiceProtocol, fastapi.Depends(get_video_manifest_service)
    ],
    video_resolution: request_deps.VideoResolution = request_deps.VideoResolution.p360,
) -> fastapi.responses.FileResponse:
    await logger.debug(
        "Request is received", video_id=video_id, video_resolution=video_resolution
    )

    video_manifest_filepath = await video_manifest_service.generate_video_manifest_file(
        video_id=video_id,
        video_resolution=video_resolution,
        s3_urls_expire_in_secs=settings.service.s3_url_expire_in_secs,
    )

    task_file_cleanup = starlette.background.BackgroundTask(
        remove_file, filepath=video_manifest_filepath
    )
    return fastapi.responses.FileResponse(
        path=video_manifest_filepath,
        filename=video_manifest_filepath.name,
        media_type="application/vnd.apple.mpegurl",
        content_disposition_type="attachment",
        background=task_file_cleanup,
    )

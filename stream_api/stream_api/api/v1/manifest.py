import typing as tp
import uuid

import fastapi
import fastapi.responses
import starlette.background

from starlette import status

from stream_api.dependencies import requests as request_deps
from stream_api.services.manifest import (
    VideoManifestFileServiceProtocol,
    get_video_manifest_service,
)
from stream_api.utils.files import remove_file


router = fastapi.APIRouter()


@router.get(
    path="/hls/manifest/{video_id}",
    summary="Get a video manifest file",
    description="Get a HLS video manifest file (.m3u8) by video file id.",
    status_code=status.HTTP_200_OK,
)
async def get_video_manifest_file(
    video_id: uuid.UUID,
    manifest_service: tp.Annotated[
        VideoManifestFileServiceProtocol, fastapi.Depends(get_video_manifest_service)
    ],
    video_resolution: request_deps.Resolution = request_deps.Resolution.p360,
) -> fastapi.responses.FileResponse:
    fp = await manifest_service.generate_video_manifest_file(
        video_id=video_id, video_resolution=video_resolution
    )

    task_file_cleanup = starlette.background.BackgroundTask(remove_file, filepath=fp)
    return fastapi.responses.FileResponse(
        path=fp,
        filename=fp.name,
        media_type="application/vnd.apple.mpegurl",
        content_disposition_type="attachment",
        background=task_file_cleanup,
    )

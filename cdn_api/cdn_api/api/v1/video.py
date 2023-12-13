import logging

from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from cdn_api.schemas import requests, responses
from cdn_api.schemas.jwt import JwtClaims
from cdn_api.services.video import (
    RemoverProtocol,
    UploaderProtocol,
    get_remover,
    get_uploader,
)
from cdn_api.utils.dependencies import (
    check_permission,
)
from cdn_api.utils.user_roles import UserRoles
from cdn_api.exceptions import CDNClientException, CDNServerException

from fastapi import APIRouter, Depends, HTTPException


logger = logging.getLogger(__name__)


router = APIRouter()

VideoFileRequestType = Annotated[
    requests.VideoUploadRequest, Depends(requests.VideoUploadRequest)
]
UploadServiceType = Annotated[UploaderProtocol, Depends(get_uploader)]
RemoveServiceType = Annotated[RemoverProtocol, Depends(get_remover)]
AdminPermissionType = Annotated[
    JwtClaims, Depends(check_permission(UserRoles.ADMIN))
]


@router.post(
    path="/upload",
    response_model=responses.UploadVideoResponse,
    summary="Upload a video file",
    description="Upload a zipped files to the CDN",
    response_description="An information of the uploaded files",
    status_code=HTTPStatus.CREATED,
)
async def upload_video(
    # _: RateLimiterType,
    # _jwt_claims: AdminPermissionType,
    video_file: VideoFileRequestType,
    service: UploadServiceType,
) -> responses.UploadVideoResponse:
    try:
        return await service.upload(video_file)
    except CDNClientException as e:
        logger.exception(f"Client error: {e}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail={'error': str(e)})
    except CDNServerException as e:
        logger.exception(f"Server error: {e}")
        # Don't send any details in order to not compromise server implementation details / technologies
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


@router.delete(
    path="/delete/{file_id: UUID}",
    summary="Delete a file",
    description="Delete a file from CDN by its ID",
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_file(
    # _jwt_claims: AdminPermissionType,
    file_id: UUID,
    service: RemoveServiceType,
) -> None:
    await service.remove(file_id)

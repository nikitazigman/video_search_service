from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from cdn_api.schemas import requests, responses
from cdn_api.schemas.jwt import JwtClaims
from cdn_api.services.files import (
    RemoverProtocol,
    UploaderProtocol,
    get_remover,
    get_uploader,
)
from cdn_api.utils.dependencies import (
    check_permission,
)
from cdn_api.utils.user_roles import UserRoles

from fastapi import APIRouter, Depends
from fastapi_pagination import Page


router = APIRouter()

ZipArchiveBodyType = Annotated[requests.UploadZipArchive, Depends()]
UploadServiceType = Annotated[UploaderProtocol, Depends(get_uploader)]
RemoveServiceType = Annotated[RemoverProtocol, Depends(get_remover)]
AdminPermissionType = Annotated[
    JwtClaims, Depends(check_permission(UserRoles.ADMIN))
]


@router.post(
    path="/upload",
    response_model=Page[responses.FileSchema],
    summary="Upload a zip archive",
    description="Upload a zipped files to the CDN",
    response_description="An information of the uploaded files",
    status_code=HTTPStatus.CREATED,
)
async def upload_files(
    # _: RateLimiterType,
    # _jwt_claims: AdminPermissionType,
    zip_archive: ZipArchiveBodyType,
    service: UploadServiceType,
) -> Page[responses.FileSchema]:
    return await service.upload(zip_archive)


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

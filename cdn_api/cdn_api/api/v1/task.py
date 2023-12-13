import logging

from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from cdn_api.schemas import responses
from cdn_api.schemas.jwt import JwtClaims

from cdn_api.utils.dependencies import (
    check_permission,
)
from cdn_api.utils.user_roles import UserRoles
from cdn_api.services.task import TaskServiceProtocol, get_task_service
from cdn_api.exceptions import CDNServerException

from fastapi import APIRouter, Depends, HTTPException


logger = logging.getLogger(__name__)

router = APIRouter()

TaskServiceType = Annotated[TaskServiceProtocol, Depends(get_task_service)]

AdminPermissionType = Annotated[
    JwtClaims, Depends(check_permission(UserRoles.ADMIN))
]


@router.get(
    path="/{task_id:uuid}",
    response_model=responses.TaskSchema,
    summary="Get task info",
    description="",
    response_description="An information about task status",
    status_code=HTTPStatus.OK,
)
async def get_task(
    task_id: UUID,
    task_service: TaskServiceType
) -> responses.TaskSchema:
    try:
        return await task_service.get_by_id(task_id)
    except CDNServerException as e:
        logger.exception(f"Server error: {e}")
        # Don't send any details in order to not compromise server implementation details / technologies
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

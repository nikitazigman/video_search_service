from typing import Protocol
from uuid import UUID

from cdn_api.schemas.responses import TaskSchema
from cdn_api.repositories.tasks import TaskRepositoryProtocol, get_task_repo
from cdn_api.utils.dependencies import DBSessionType


class TaskServiceProtocol(Protocol):

    async def get_by_id(self, task_id: UUID) -> TaskSchema:
        ...


class TaskService(TaskServiceProtocol):

    def __init__(self, task_repository: TaskRepositoryProtocol) -> None:
        self.task_repository = task_repository

    async def get_by_id(self, task_id: UUID) -> TaskSchema:
        return await self.task_repository.get_by_id(task_id)


def get_task_service(
    sql_session: DBSessionType
) -> TaskServiceProtocol:
    return TaskService(get_task_repo(sql_session))

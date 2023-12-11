from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from cdn_api.models.task import Status, Task
from cdn_api.schemas.responses import TaskSchema

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession


class TaskRepositoryProtocol(Protocol):
    async def get_by_id(self, task_id: UUID) -> TaskSchema:
        ...

    async def get_all_info(self) -> Page[TaskSchema]:
        ...

    async def insert(self, status: Status, video_meta_id: UUID) -> TaskSchema:
        ...

    async def delete(self, task_id: UUID) -> None:
        ...


class TaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, task_id: UUID) -> TaskSchema:
        select_stmt = select(Task).where(Task.id == task_id)
        task_model = await self.session.scalar(select_stmt)
        return TaskSchema.model_validate(task_model)

    def _transformer(self, models: Sequence[Task]) -> list[TaskSchema]:
        return [TaskSchema.model_validate(model) for model in models]

    async def get_all_info(self) -> Page[TaskSchema]:
        files_info = await paginate(
            self.session,
            select(Task),
            Params(),
            transformer=self._transformer,
        )
        return files_info

    async def insert(self, status: Status, video_meta_id: UUID) -> TaskSchema:
        insert_stmt = (
            insert(Task)
            .values(status=status, video_meta_id=video_meta_id)
            .returning(Task)
        )
        video_meta_model = await self.session.scalar(insert_stmt)
        return TaskSchema.model_validate(video_meta_model)

    async def delete(self, task_id: UUID) -> None:
        delete_stmt = delete(Task).where(Task.id == task_id)
        await self.session.execute(delete_stmt)


def get_task_repo(session: AsyncSession) -> TaskRepositoryProtocol:
    return TaskRepository(session)

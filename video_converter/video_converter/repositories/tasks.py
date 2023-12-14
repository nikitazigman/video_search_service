from typing import Protocol
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from video_converter.models.task import Status, Task
from video_converter.schemas.task import TaskSchema
from video_converter.exceptions import VideoConverterDBError


class TaskRepositoryProtocol(Protocol):
    async def update(self, task_id: UUID, status: Status) -> TaskSchema:
        ...


class TaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def update(self, task_id: UUID, status: Status) -> TaskSchema:
        try:
            update_stmt = (
                update(Task).where(Task.id == task_id).values(status=status).returning(Task)
            )
            task_model = await self.session.scalar(update_stmt)
            return TaskSchema.model_validate(task_model)
        except (SQLAlchemyError, IOError) as e:
            raise VideoConverterDBError from e


def get_task_repo(session: AsyncSession) -> TaskRepositoryProtocol:
    return TaskRepository(session)

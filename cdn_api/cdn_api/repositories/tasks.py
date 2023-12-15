import logging
from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from cdn_api.models.task import Status, Task
from cdn_api.schemas.responses import TaskSchema
from cdn_api.exceptions import DBClientException, DBServerException

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, ArgumentError, SQLAlchemyError
from pydantic import ValidationError


logger = logging.getLogger(__name__)


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
        logger.info(f"Obtaining task: {task_id}")
        try:
            select_stmt = select(Task).where(Task.id == task_id)
            task_model = await self.session.scalar(select_stmt)
            return TaskSchema.model_validate(task_model)
        except (SQLAlchemyError, IOError) as e:
            raise DBServerException from e

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
        logger.info(f"Inserting new task. status: {status}, video_meta_id: {video_meta_id}")
        try:
            insert_stmt = (
                insert(Task)
                .values(status=status, video_meta_id=video_meta_id)
                .returning(Task)
            )
            video_meta_model = await self.session.scalar(insert_stmt)
            return TaskSchema.model_validate(video_meta_model)
        except (IntegrityError, ValidationError, ArgumentError) as e:
            raise DBClientException("Incorrect data was provided!") from e
        # Any other sql alchemy or network errors should be considered as server failure
        except (SQLAlchemyError, IOError) as e:
            raise DBServerException from e

    async def delete(self, task_id: UUID) -> None:
        logger.info(f"Deleting task: {task_id}")
        delete_stmt = delete(Task).where(Task.id == task_id)
        await self.session.execute(delete_stmt)


def get_task_repo(session: AsyncSession) -> TaskRepositoryProtocol:
    return TaskRepository(session)

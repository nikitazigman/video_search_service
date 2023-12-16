import asyncio
import logging

from types import TracebackType
from typing import Protocol, Self

from cdn_api.message_queue.message_queue import (
    MessageQueueProtocol,
    get_message_queue,
)
from cdn_api.repositories.s3 import S3RepoProtocol, get_s3_repo
from cdn_api.repositories.tasks import TaskRepositoryProtocol, get_task_repo
from cdn_api.repositories.video_meta import (
    VideoMetaRepositoryProtocol,
    get_video_meta_repo,
)
from cdn_api.utils.dependencies import (
    DBSessionType,
    RabbitMQChannelType,
    S3ClientType,
)

from aio_pika.abc import AbstractRobustChannel, AbstractTransaction
from miniopy_async import Minio  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger(__name__)


class VideoUOWProtocol(Protocol):
    s3_repo: S3RepoProtocol
    video_meta_repo: VideoMetaRepositoryProtocol
    task_repo: TaskRepositoryProtocol
    message_queue: MessageQueueProtocol

    async def __aenter__(self) -> Self:
        ...

    async def __aexit__(
        self,
        exc_type: type[Exception],
        exception: Exception,
        traceback: TracebackType,
    ) -> None:
        ...

    async def commit(self) -> None:
        ...

    async def rollback(self) -> None:
        ...


class VideoUOW:
    def __init__(
        self,
        sql_session: AsyncSession,
        s3_client: Minio,
        rabbit_channel: AbstractRobustChannel,
    ):
        self.rabbit_transaction: None | AbstractTransaction = None
        self.sql_session = sql_session
        self.s3_client = s3_client
        self.rabbit_channel = rabbit_channel

        self.video_meta_repo = get_video_meta_repo(self.sql_session)
        self.task_repo = get_task_repo(self.sql_session)
        self.s3_repo = get_s3_repo(s3_client)
        self.message_queue = get_message_queue(rabbit_channel)

    async def __aenter__(self) -> Self:
        self.rabbit_transaction = self.rabbit_channel.transaction()
        await self.rabbit_transaction.select()
        return self

    async def __aexit__(
        self,
        exc_type: type[Exception],
        exception: Exception,
        traceback: TracebackType,
    ) -> None:
        if exception is not None:
            await self.rollback()
            raise exception

    async def commit(self) -> None:
        logger.info("Commit video uow transaction")
        if self.rabbit_transaction is None:
            raise RuntimeError("RabbitMQ transaction is not initialized")
        await asyncio.gather(
            self.rabbit_transaction.commit(),
            self.sql_session.commit(),
        )

    async def rollback(self) -> None:
        logger.debug("Rollback video uow transaction")
        if self.rabbit_transaction is None:
            raise RuntimeError("RabbitMQ transaction is not initialized")

        await asyncio.gather(
            self.rabbit_transaction.rollback(),
            self.sql_session.rollback(),
        )


def get_file_uow(
    sql_session: DBSessionType,
    s3_client: S3ClientType,
    rabbit_channel: RabbitMQChannelType,
) -> VideoUOWProtocol:
    return VideoUOW(
        sql_session=sql_session,
        s3_client=s3_client,
        rabbit_channel=rabbit_channel,
    )

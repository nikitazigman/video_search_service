from typing import Protocol

from cdn_api.configs.settings import get_settings
from cdn_api.schemas.responses import UploadVideoResponse

from aio_pika.abc import AbstractRobustChannel
from aio_pika.message import Message


class MessageQueueProtocol(Protocol):
    async def send_message(self, message: UploadVideoResponse) -> None:
        ...


class MessageQueue:
    def __init__(self, channel: AbstractRobustChannel, routing_key: str):
        self.channel = channel
        self.routing_key = routing_key

    async def send_message(self, message: UploadVideoResponse) -> None:
        pika_message = Message(body=message.model_dump_json().encode())
        await self.channel.default_exchange.publish(
            routing_key=self.routing_key, message=pika_message
        )


def get_message_queue(channel: AbstractRobustChannel) -> MessageQueueProtocol:
    settings = get_settings()
    return MessageQueue(
        channel=channel, routing_key=settings.worker_queue_name
    )

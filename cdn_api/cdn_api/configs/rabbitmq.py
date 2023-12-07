from cdn_api.configs.settings import Settings

from aio_pika import connect_robust
from aio_pika.abc import AbstractChannel, AbstractRobustConnection


_connection: None | AbstractRobustConnection = None


async def init_rabbitmq(settings: Settings) -> None:
    global _connection
    _connection = await connect_robust(settings.rabbitmq_dsn())


async def get_rabbitmq_channel() -> AbstractChannel:
    global _connection

    if _connection is None:
        raise RuntimeError("RabbitMQ is not initialized")

    async with _connection:
        yield await _connection.channel(publisher_confirms=False)


async def close_rabbitmq() -> None:
    global _connection

    if _connection is not None:
        await _connection.close()
        _connection = None

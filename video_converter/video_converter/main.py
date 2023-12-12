import asyncio

from faststream import FastStream
from faststream.rabbit import RabbitBroker

from video_converter.api.v1.router import router
from video_converter.configs.minio import init_s3_client
from video_converter.configs.postgres import close_async_engine, init_async_engine
from video_converter.configs.settings import get_settings

broker = RabbitBroker()
app = FastStream(broker=broker)


@app.on_startup
async def on_startup() -> None:
    settings = get_settings()
    init_s3_client(settings=settings)
    await init_async_engine(settings=settings)

    await broker.connect(
        host=settings.rabbitmq_host,
        port=settings.rabbitmq_port,
        login=settings.rabbitmq_user,
        password=settings.rabbitmq_password,
        virtualhost=settings.rabbitmq_vhost,
    )


@app.on_shutdown
async def on_shutdown() -> None:
    await broker.close()
    await close_async_engine()


broker.include_router(router)

if __name__ == "__main__":
    asyncio.run(app.run())

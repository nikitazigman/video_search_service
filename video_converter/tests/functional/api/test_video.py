from pathlib import Path
from uuid import uuid4

import pytest  # type: ignore
from faststream.rabbit import RabbitBroker
from miniopy_async import Minio  # type: ignore
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from video_converter.models.task import Task
from video_converter.models.video import VideoMeta
from video_converter.schemas.input import VideoInputSchema
from video_converter.schemas.task import TaskSchema
from video_converter.schemas.video import VideoSchema

pytestmark = pytest.mark.asyncio


async def test_create_video(
    rabbitmq_channel: RabbitBroker,
    db_session: AsyncSession,
    minio_client: Minio,
):
    video_id = uuid4()
    original_bucket = "original"
    hlc_bucket = "hlc"

    if not await minio_client.bucket_exists(original_bucket):
        await minio_client.make_bucket(original_bucket)

    test_video = Path(__file__).parent.parent / "files/test.mp4"
    await minio_client.fput_object(
        bucket_name=original_bucket,
        object_name=test_video.name,
        file_path=str(test_video),
    )
    video_insert_stmt = (
        insert(VideoMeta)
        .values(
            video_id=video_id,
            name=test_video.name,
            bucket_original=original_bucket,
            bucket_hlc=hlc_bucket,
        )
        .returning(VideoMeta)
    )
    video_model = await db_session.scalar(video_insert_stmt)
    video_schema = VideoSchema.model_validate(video_model)
    task_insert_stmt = (
        insert(Task)
        .values(status="pending", video_meta_id=video_schema.id)
        .returning(Task)
    )
    task_model = await db_session.scalar(task_insert_stmt)
    task_schema = TaskSchema.model_validate(task_model)
    testy_message = VideoInputSchema(video_meta=video_schema, task=task_schema)
    await db_session.commit()

    await rabbitmq_channel.publish(
        message=testy_message.model_dump(), queue="video_processing"
    )

    # # test minio
    assert await minio_client.bucket_exists(hlc_bucket)
    folder_name = video_schema.name.replace(".mp4", "")
    bucket_objects = await minio_client.list_objects(
        hlc_bucket, recursive=True, prefix=folder_name
    )
    objects_names = [obj.object_name for obj in bucket_objects]

    assert f"{folder_name}/hlc-1080/{folder_name}.m3u8" in objects_names
    assert f"{folder_name}/hlc-720/{folder_name}.m3u8" in objects_names
    assert f"{folder_name}/hlc-360/{folder_name}.m3u8" in objects_names

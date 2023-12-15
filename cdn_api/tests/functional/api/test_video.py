from pathlib import Path
from uuid import uuid4

from cdn_api.configs.settings import get_settings
from cdn_api.models.task import Task
from cdn_api.models.video import VideoMeta

import pytest  # type: ignore

from aio_pika import Channel
from httpx import AsyncClient
from miniopy_async import Minio  # type: ignore
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


pytestmark = pytest.mark.asyncio


async def test_create_video(
    api_client: AsyncClient,
    rabbitmq_channel: Channel,
    db_session: AsyncSession,
    minio_client: Minio,
):
    settings = get_settings()
    video_id = str(uuid4())
    test_video = Path(__file__).parent.parent / "files/test.mp4"
    with test_video.open("rb") as f:
        response = await api_client.post(
            "/api/v1/video/upload",
            files={
                "file": (test_video.name, f.read()),
            },
            data={
                "video_id": video_id,
            },
        )

    # test response
    assert response.status_code == 201

    response_data = response.json()
    video_meta = response_data["video_meta"]
    assert video_meta["name"] == test_video.name
    assert video_meta["video_id"] == video_id
    assert video_meta["bucket_original"] == settings.original_bucket
    assert video_meta["bucket_hlc"] == settings.hlc_bucket

    task = response_data["task"]
    assert task["status"] == "pending"
    assert task["video_meta_id"] == video_meta["id"]

    # test sql db
    video_select_stmt = select(VideoMeta).where(VideoMeta.video_id == video_id)
    video_model = await db_session.scalar(video_select_stmt)

    assert video_model is not None
    assert video_model.name == test_video.name
    assert str(video_model.video_id) == video_id
    assert video_model.bucket_original == settings.original_bucket
    assert video_model.bucket_hlc == settings.hlc_bucket

    task_select_stmt = select(Task).where(Task.video_meta_id == video_model.id)
    task_model = await db_session.scalar(task_select_stmt)
    assert task_model is not None
    assert task_model.status == "pending"
    assert task_model.video_meta_id == video_model.id

    # test minio
    assert await minio_client.bucket_exists(settings.original_bucket)
    bucket_objects = await minio_client.list_objects(settings.original_bucket)
    objects_names = [obj.object_name for obj in bucket_objects]
    assert test_video.name in objects_names

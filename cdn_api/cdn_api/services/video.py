from datetime import datetime
from typing import Annotated, Protocol
from uuid import UUID

from cdn_api.models.task import Status
from cdn_api.schemas.responses import UploadVideoResponse
from cdn_api.uow.video import VideoUOWProtocol, get_file_uow
from cdn_api.utils.dependencies import SettingsType

from fastapi import Depends, UploadFile


class UploaderProtocol(Protocol):
    async def upload(self, video_body: UploadFile) -> UploadVideoResponse:
        ...


class RemoverProtocol(Protocol):
    async def remove(self, video_id: UUID) -> None:
        ...


class VideoService:
    def __init__(
        self, uow: VideoUOWProtocol, original_bucket: str, hlc_bucket: str
    ) -> None:
        self.uow = uow
        self.original_bucket = original_bucket
        self.hlc_bucket = hlc_bucket

    async def remove(self, video_id: UUID) -> None:
        return None

    async def upload(self, video_body: UploadFile) -> UploadVideoResponse:
        filename = video_body.filename or f"unknown_{datetime.now()}.mp4"
        original_bucket = self.original_bucket

        async with self.uow as uow:
            video_schema = await uow.video_meta_repo.insert(
                name=filename,
                original_bucket=self.original_bucket,
                bucket_hlc=self.hlc_bucket,
            )
            task_schema = await uow.task_repo.insert(
                status=Status.PENDING, video_meta_id=video_schema.id
            )
            upload_video_response = UploadVideoResponse(
                task=task_schema, video_meta=video_schema
            )
            await uow.message_queue.send_message(upload_video_response)

            await uow.s3_repo.upload_video(
                bucket_name=original_bucket,
                file_name=filename,
                file=video_body,
            )
            await uow.commit()

        return UploadVideoResponse(task=task_schema, video_meta=video_schema)


VideoUOWType = Annotated[VideoUOWProtocol, Depends(get_file_uow)]


def get_uploader(
    uow: VideoUOWType, settings: SettingsType
) -> UploaderProtocol:
    return VideoService(uow, settings.original_bucket, settings.hlc_bucket)


def get_remover(uow: VideoUOWType, settings: SettingsType) -> RemoverProtocol:
    return VideoService(uow, settings.original_bucket, settings.hlc_bucket)

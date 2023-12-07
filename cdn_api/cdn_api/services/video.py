from typing import Annotated, Protocol
from uuid import UUID

from cdn_api.models.task import Status
from cdn_api.schemas.requests import UploadVideo
from cdn_api.schemas.responses import UploadVideoResponse
from cdn_api.uow.video import VideoUOWProtocol, get_file_uow

from fastapi import Depends


class UploaderProtocol(Protocol):
    async def upload(self, video_body: UploadVideo) -> UploadVideoResponse:
        ...


class RemoverProtocol(Protocol):
    async def remove(self, video_id: UUID) -> None:
        ...


class VideoService:
    def __init__(self, uow: VideoUOWProtocol) -> None:
        self.uow = uow

    async def remove(self, video_id: UUID) -> None:
        return None

    async def upload(self, video_body: UploadVideo) -> UploadVideoResponse:
        async with self.uow as uow:
            video_schema = await uow.video_meta_repo.insert(
                name=video_body.name, bucket=video_body.bucket
            )
            task_schema = await uow.task_repo.insert(
                status=Status.PENDING, video_meta_id=video_schema.id
            )
            await uow.s3_repo.upload_video(
                bucket_name=video_body.bucket,
                file_name=str(video_schema.id),
                file=video_body.video,
            )
            await uow.commit()

        return UploadVideoResponse(task=task_schema, video_meta=video_schema)


VideoUOWType = Annotated[VideoUOWProtocol, Depends(get_file_uow)]


def get_uploader(uow: VideoUOWType) -> UploaderProtocol:
    return VideoService(uow)


def get_remover(uow: VideoUOWType) -> RemoverProtocol:
    return VideoService(uow)

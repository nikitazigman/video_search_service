import logging

from datetime import datetime
from pathlib import Path
from typing import Protocol

from faststream import Depends

from video_converter.configs.settings import get_settings
from video_converter.models.task import Status
from video_converter.schemas.input import VideoInputSchema
from video_converter.uow.video import VideoUOW, VideoUOWProtocol, get_file_uow
from video_converter.utils.converter import (
    VideoConverter,
    VideoConverterProtocol,
    get_video_converter,
)


logger = logging.getLogger(__name__)


class VideoServiceProtocol(Protocol):
    async def process(self, body: VideoInputSchema) -> None:
        ...


class VideoService:
    def __init__(
        self,
        uow: VideoUOWProtocol,
        video_converter: VideoConverterProtocol,
        tmp_folder: Path,
    ) -> None:
        self.uow = uow
        self.tmp_folder = tmp_folder
        self.video_converter = video_converter

    def remove_dir(self, path: Path) -> None:
        try:
            for item in path.iterdir():
                if item.is_dir():
                    self.remove_dir(item)
                else:
                    item.unlink()
            path.rmdir()
        except OSError as e:
            logger.exception(f"Unexpected error during clean up of directory: {e}")

    async def process(self, body: VideoInputSchema) -> None:
        tmp_folder = self.tmp_folder / str(datetime.now().timestamp())

        input_file = tmp_folder / f"input/{body.video_meta.name}"
        video_name = body.video_meta.name.replace(".mp4", "")
        output_folder = tmp_folder / f"output/{video_name}"

        output_file_360 = output_folder / f"hlc-360/{video_name}.m3u8"
        output_file_720 = output_folder / f"hlc-720/{video_name}.m3u8"
        output_file_1080 = output_folder / f"hlc-1080/{video_name}.m3u8"

        async with self.uow as uow:
            await uow.task_repo.update(
                task_id=body.task.id,
                status=Status.PROCESSING,
            )
            await uow.commit()

            await uow.s3_repo.download_video(
                bucket_name=body.video_meta.bucket_original,
                file_name=body.video_meta.name,
                path=input_file,
            )
            await self.video_converter.convert(
                file_path=input_file,
                frame_size="640x360",
                output_path=output_file_360,
            )
            await self.video_converter.convert(
                file_path=input_file,
                frame_size="1280x720",
                output_path=output_file_720,
            )
            await self.video_converter.convert(
                file_path=input_file,
                frame_size="1920x1080",
                output_path=output_file_1080,
            )

            await uow.s3_repo.upload_chunks(
                bucket_name="hlc",
                folder=output_folder,
            )

            await uow.task_repo.update(
                task_id=body.task.id,
                status=Status.DONE,
            )

            await uow.commit()

        self.remove_dir(tmp_folder)


def get_video_service(
    uow: VideoUOW = Depends(get_file_uow),
    converter: VideoConverter = Depends(get_video_converter),
) -> VideoService:
    settings = get_settings()
    return VideoService(
        uow=uow, tmp_folder=settings.tmp_folder, video_converter=converter
    )

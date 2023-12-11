from faststream import Depends
from faststream.rabbit import RabbitRouter

from video_converter.schemas.input import VideoInputSchema
from video_converter.services.video import VideoService, get_video_service

router = RabbitRouter()


@router.subscriber("video_processing")
async def process_video(
    task_body: VideoInputSchema,
    service: VideoService = Depends(get_video_service),
) -> None:
    await service.process(task_body)

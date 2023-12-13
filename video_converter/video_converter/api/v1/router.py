import logging

from faststream import Depends
from faststream.rabbit import RabbitRouter

from video_converter.schemas.input import VideoInputSchema
from video_converter.services.video import VideoService, get_video_service
from video_converter.exceptions import VideoConverterMinioException

logger = logging.getLogger(__name__)

router = RabbitRouter()


@router.subscriber("video_processing")
async def process_video(
    task_body: VideoInputSchema,
    service: VideoService = Depends(get_video_service),
) -> None:
    try:
        await service.process(task_body)
    except VideoConverterError as e:
        logger.exception(f"Couldn't process video: {e}")

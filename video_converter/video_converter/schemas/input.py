from pydantic import BaseModel

from video_converter.schemas.task import TaskSchema
from video_converter.schemas.video import VideoSchema


class VideoInputSchema(BaseModel):
    video_meta: VideoSchema
    task: TaskSchema

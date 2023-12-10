from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class VideoSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: UUID
    bucket: str
    name: str
    created_at: datetime
    updated_at: datetime


class TaskSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: UUID
    video_meta_id: UUID
    status: str


class UploadVideoResponse(BaseModel):
    video_meta: VideoSchema
    task: TaskSchema

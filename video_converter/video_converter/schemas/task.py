from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TaskSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: UUID
    video_meta_id: UUID
    status: str

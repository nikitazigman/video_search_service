from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class VideoSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: UUID

    name: str
    bucket_original: str
    bucket_hlc: str

    created_at: datetime
    updated_at: datetime

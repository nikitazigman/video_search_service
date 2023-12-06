from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class FileSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: UUID
    name: str
    path: str
    version: int
    created_at: datetime
    updated_at: datetime

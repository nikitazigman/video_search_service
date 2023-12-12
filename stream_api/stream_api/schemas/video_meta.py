import uuid

import pydantic


class VideoMeta(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    id: uuid.UUID
    name: str
    bucket_original: str
    bucket_hlc: str

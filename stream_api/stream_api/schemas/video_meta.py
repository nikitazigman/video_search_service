import uuid

import pydantic


class VideoMeta(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    name: str
    bucket_original: str
    bucket_hlc: str
    video_id: uuid.UUID

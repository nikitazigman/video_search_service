import enum
import uuid

import pydantic


class Resolution(enum.IntEnum):
    p360 = 360
    p720 = 720
    p1080 = 1080


class VideoFile(pydantic.BaseModel):
    id: uuid.UUID

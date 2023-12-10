from enum import StrEnum

from cdn_api.models.common import (
    BaseModel,
    TimeStampedMixin,
    UUIDMixin,
)
from cdn_api.models.video import VideoMeta

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class Status(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class Task(BaseModel, TimeStampedMixin, UUIDMixin):
    __tablename__ = "task"

    video_meta_id: Mapped[VideoMeta] = mapped_column(
        ForeignKey("video_meta.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[Enum] = mapped_column(Enum(Status), nullable=False)

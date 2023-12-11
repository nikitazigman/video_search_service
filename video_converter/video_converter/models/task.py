from enum import StrEnum

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from video_converter.models.common import (
    BaseModel,
    TimeStampedMixin,
    UUIDMixin,
)
from video_converter.models.video import VideoMeta


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

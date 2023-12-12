from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from video_converter.models.common import (
    BaseModel,
    TimeStampedMixin,
    UUIDMixin,
)


class VideoMeta(BaseModel, TimeStampedMixin, UUIDMixin):
    __tablename__ = "video_meta"

    bucket: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"Video {self.bucket}/{self.name}"

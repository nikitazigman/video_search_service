from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from video_converter.models.common import (
    BaseModel,
    TimeStampedMixin,
    UUIDMixin,
)


class VideoMeta(BaseModel, TimeStampedMixin, UUIDMixin):
    __tablename__ = "video_meta"

    bucket_original: Mapped[str] = mapped_column(
        String(512), unique=False, nullable=False
    )
    video_id: Mapped[UUID] = mapped_column(UUID, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)

    bucket_hlc: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"Video {self.bucket_original}/{self.name}"

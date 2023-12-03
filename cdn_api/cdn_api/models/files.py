from cdn_api.models.common import (
    BaseModel,
    TimeStampedMixin,
    UUIDMixin,
)

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class File(BaseModel, TimeStampedMixin, UUIDMixin):
    __tablename__ = "file_meta"

    path: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    def __repr__(self) -> str:
        return f"<file {self.path}>"

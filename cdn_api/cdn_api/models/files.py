from cdn_api.models.common import (
    BaseModel,
    TimeStampedMixin,
    UUIDMixin,
)

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class File(BaseModel, TimeStampedMixin, UUIDMixin):
    __tablename__ = "file_meta"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    path: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<file {self.path}>"

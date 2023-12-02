import uuid

from datetime import datetime

from cdn_api.configs.settings import get_settings

from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


settings = get_settings()


class BaseModel(AsyncAttrs, DeclarativeBase):
    metadata = MetaData(schema=settings.postgres_schema)


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(),
        primary_key=True,
        default=uuid.uuid4,
    )


class TimeStampedMixin:
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now()
    )

from cdn_api.models.common import (
    BaseModel,
    TimeStampedMixin,
    UUIDMixin,
)

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Location(BaseModel, TimeStampedMixin, UUIDMixin):
    __tablename__ = "locations"

    region: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self) -> str:
        return f"<Location {self.region}-{self.country}-{self.city}>"


class EdgeNode(BaseModel, TimeStampedMixin, UUIDMixin):
    __tablename__ = "edge_nodes"

    ip_address: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(255), nullable=False)

    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"))
    location: Mapped[Location] = relationship()

    def __repr__(self) -> str:
        return f"<EdgeNode {self.ip_address}:{self.port}>"

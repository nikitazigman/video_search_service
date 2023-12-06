from uuid import UUID
from enum import StrEnum, auto
from pydantic import BaseModel, ConfigDict, IPvAnyAddress


class Location(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: UUID
    region: str
    country: str
    city: str


class EdgeNodeStatus(StrEnum):
    online = auto()
    offline = auto()
    busy = auto()
    maintenance = auto()
    error = auto()


class EdgeNode(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: UUID
    ip_address: IPvAnyAddress
    port: int
    name: str
    status: EdgeNodeStatus
    location: Location

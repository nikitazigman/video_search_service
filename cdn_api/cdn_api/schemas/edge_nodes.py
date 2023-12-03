from uuid import UUID

from pydantic import BaseModel, ConfigDict, IPvAnyAddress


class Location(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: UUID
    region: str
    country: str
    city: str


class EdgeNode(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: UUID
    name: str
    ip_address: IPvAnyAddress
    port: int
    location: Location

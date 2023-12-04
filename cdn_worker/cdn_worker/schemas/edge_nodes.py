import datetime
import enum
import uuid

import pydantic


class EdgeNodeStatus(enum.StrEnum):
    online = enum.auto()
    offline = enum.auto()
    busy = enum.auto()
    maintenance = enum.auto()
    error = enum.auto()


class EdgeNode(pydantic.BaseModel):
    id: uuid.UUID
    name: str
    ip_address: pydantic.IPvAnyAddress
    port: int
    status: EdgeNodeStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime

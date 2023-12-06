from pathlib import Path

from pydantic import BaseModel, ConfigDict


class InsertFileSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    path: Path

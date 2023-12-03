from pydantic import BaseModel, ConfigDict


class InsertFileSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    path: str

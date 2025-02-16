from typing import Literal

from pydantic import BaseModel


class HealthStatusModel(BaseModel):
    database: bool
    redis: bool


class HealthResponse(BaseModel):
    health: Literal["ok", "partial"]
    status: HealthStatusModel

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class LineStatus(str, Enum):
    PROVISIONED = "PROVISIONED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DELETED = "DELETED"


class LineCreate(BaseModel):
    msisdn: str
    plan_name: str


class LineUpdateStatus(BaseModel):
    status: LineStatus


class LineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    msisdn: str
    plan_name: str
    status: LineStatus
    created_at: datetime

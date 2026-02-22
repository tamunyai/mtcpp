from datetime import datetime
from enum import Enum

from pydantic import BaseModel


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
    id: int
    account_id: int
    msisdn: str
    plan_name: str
    status: LineStatus
    created_at: datetime

    class Config:
        from_attributes = True

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr


class AccountStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    CLOSED = "CLOSED"


class AccountCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    status: AccountStatus = AccountStatus.ACTIVE


class AccountUpdate(BaseModel):
    full_name: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    status: Optional[AccountStatus]


class AccountResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    status: AccountStatus
    created_at: datetime

    class Config:
        from_attributes = True

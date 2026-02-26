from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: UUID


class SessionResponse(BaseModel):
    access_token: str
    refresh_token: UUID
    expires_in: int
    expires_at: Optional[int] = None
    token_type: str = "bearer"

    user: UserResponse

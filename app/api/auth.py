from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException, UnauthorizedException
from app.db.session import get_db
from app.models.auth import RefreshToken
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshTokenRequest, SessionResponse
from app.services.auth_service import authenticate_user, generate_session

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=SessionResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, request.username, request.password)

    if not user:
        raise UnauthorizedException(detail="Invalid credentials")

    return generate_session(db, user)


@router.post("/refresh", response_model=SessionResponse)
def refresh(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    refresh_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.id == request.refresh_token, RefreshToken.revoked == 0)
        .first()
    )

    if not refresh_token:
        raise UnauthorizedException(detail="Invalid refresh token")

    if refresh_token.expires_at < datetime.now():
        raise UnauthorizedException(detail="Refresh token expired")

    user = db.query(User).filter(User.id == refresh_token.user_id).first()
    if not user:
        raise NotFoundException(detail="User not found")

    # revoke old refresh token (rotation)
    refresh_token.revoked = 1
    db.commit()

    return generate_session(db, user)

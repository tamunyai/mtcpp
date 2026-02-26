from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.models.auth import RefreshToken
from app.models.user import User
from app.schemas.user import UserResponse


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


def generate_session(db: Session, user: User):
    access_token, access_expiry = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    refresh_expiry = datetime.now(timezone.utc) + timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )
    refresh_token = RefreshToken(
        user_id=user.id,
        expires_at=refresh_expiry,
    )

    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": str(refresh_token.id),
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        "expires_at": int(access_expiry.timestamp()),
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
    }

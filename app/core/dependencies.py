from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_token
from app.schemas.user import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_token(token)
        username = payload.get("sub")
        role = payload.get("role")

        if username is None:
            raise UnauthorizedException(detail="Invalid token")

        return {"username": username, "role": role}

    except JWTError:
        raise UnauthorizedException(detail="Invalid token")


def require_role(required_role: UserRole):
    def role_checker(user=Depends(get_current_user)):
        try:
            user_role = UserRole(user["role"])

        except Exception:
            raise UnauthorizedException(detail="Invalid token role")

        if user_role != required_role:
            raise ForbiddenException(detail="Insufficient permissions")

        return user

    return role_checker

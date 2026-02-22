from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from app.db.base import Base
from app.schemas.account import AccountStatus


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)
    status = Column(String, nullable=False, default=AccountStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

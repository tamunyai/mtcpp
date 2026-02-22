from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.db.base import Base
from app.schemas.line import LineStatus


class Line(Base):
    __tablename__ = "lines"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    msisdn = Column(String, unique=True, nullable=False)
    plan_name = Column(String, nullable=False)
    status = Column(String, nullable=False, default=LineStatus.PROVISIONED)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

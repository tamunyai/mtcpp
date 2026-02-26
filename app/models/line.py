from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.schemas.line import LineStatus


class Line(Base):
    __tablename__ = "lines"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, default=uuid4)
    account_id: Mapped[UUID] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    msisdn: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    plan_name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[LineStatus] = mapped_column(
        Enum(LineStatus), nullable=False, default=LineStatus.PROVISIONED
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

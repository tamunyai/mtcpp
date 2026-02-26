from datetime import date, datetime
from enum import Enum
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.audit import Audit

logger = get_logger()


def _sanitize(value: Any) -> Any:
    """Recursively convert common non-JSON types to JSON-serializable forms.

    - UUID -> str
    - datetime/date -> ISO string
    - Enum -> value
    - dict/list/tuple -> recursive
    - other unknowns -> str()
    """
    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, UUID):
        return str(value)

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, dict):
        return {k: _sanitize(v) for k, v in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [_sanitize(v) for v in value]

    # Fallback to string representation
    try:
        return str(value)
    except Exception:
        return None


def record_audit(
    db: Session,
    actor: dict | str | None,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    old: dict | None = None,
    new: dict | None = None,
):
    actor_name = None

    if isinstance(actor, dict):
        actor_name = actor.get("username")

    elif isinstance(actor, str):
        actor_name = actor

    entry = Audit(
        actor=actor_name,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id is not None else None,
        old=_sanitize(old),
        new=_sanitize(new),
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    logger.info(f"Audit recorded: {action} {resource_type}/{resource_id} by {actor_name}")
    return entry

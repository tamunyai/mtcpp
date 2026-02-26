from typing import Set

from app.schemas.line import LineStatus

# Define allowed transitions for LineStatus
ALLOWED_TRANSITIONS: dict[LineStatus, Set[LineStatus]] = {
    LineStatus.PROVISIONED: {LineStatus.ACTIVE, LineStatus.SUSPENDED, LineStatus.DELETED},
    LineStatus.ACTIVE: {LineStatus.SUSPENDED, LineStatus.DELETED},
    LineStatus.SUSPENDED: {LineStatus.ACTIVE, LineStatus.DELETED},
    LineStatus.DELETED: set(),
}


def _to_line_status(value) -> LineStatus | None:
    if isinstance(value, LineStatus):
        return value

    try:
        return LineStatus(value)
    except Exception:
        return None


def can_transition(current, target) -> bool:
    """Return True if a transition from current -> target is allowed."""
    cur = _to_line_status(current)
    tgt = _to_line_status(target)

    if cur is None or tgt is None:
        return False

    return tgt in ALLOWED_TRANSITIONS.get(cur, set())


def is_commissionable(current) -> bool:
    """Return True if a line in `current` status can be commissioned (i.e. PROVISIONED)."""
    cur = _to_line_status(current)
    return cur == LineStatus.PROVISIONED

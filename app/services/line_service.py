import time
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException, NotFoundException
from app.core.logging import get_logger
from app.core.state import can_transition, is_commissionable
from app.models.account import Account
from app.models.line import Line
from app.schemas.line import LineCreate, LineResponse, LineStatus
from app.services.audit_service import record_audit

logger = get_logger()


def create_line(
    db: Session, account_id: UUID, line_data: LineCreate, actor: dict | str | None = None
):
    account = db.query(Account).filter(Account.id == account_id).first()

    if not account:
        raise NotFoundException(detail="Account not found")

    line = Line(
        account_id=account_id,
        msisdn=line_data.msisdn,
        plan_name=line_data.plan_name,
        status=LineStatus.PROVISIONED,
    )

    db.add(line)
    db.commit()
    db.refresh(line)

    logger.info(f"Line created: {line.id} for Account {account_id}")

    try:
        new = LineResponse.model_validate(line).model_dump()
        record_audit(db, actor, "create_line", "line", str(line.id), old=None, new=new)
    except Exception:
        logger.debug("Failed to record audit for line creation")

    return line


def get_lines_by_account(db: Session, account_id: UUID):
    return db.query(Line).filter(Line.account_id == account_id).all()


def update_line_status(
    db: Session, line_id: UUID, new_status: str, actor: dict | str | None = None
):
    line = db.query(Line).filter(Line.id == line_id).first()

    if not line:
        raise NotFoundException(detail="Line not found")

    # Validate allowed state transition centrally
    if not can_transition(line.status, new_status):
        raise BadRequestException(
            detail=f"Invalid status transition: {line.status} -> {new_status}"
        )

    try:
        old = LineResponse.model_validate(line).model_dump()
    except Exception:
        old = None

    line.status = new_status
    db.commit()
    db.refresh(line)

    logger.info(f"Line status updated: Line {line.id} -> {new_status}")

    try:
        new = LineResponse.model_validate(line).model_dump()
        record_audit(db, actor, "update_line_status", "line", str(line.id), old=old, new=new)
    except Exception:
        logger.debug("Failed to record audit for line status update")
    return line


def delete_line(db: Session, line_id: UUID, actor: dict | str | None = None):
    line = db.query(Line).filter(Line.id == line_id).first()

    if not line:
        raise NotFoundException(detail="Line not found")

    try:
        old = LineResponse.model_validate(line).model_dump()
    except Exception:
        old = None

    line.status = LineStatus.DELETED
    db.commit()

    logger.info(f"Line deleted: Line {line.id}")

    try:
        new = LineResponse.model_validate(line).model_dump()
        record_audit(db, actor, "delete_line", "line", str(line.id), old=old, new=new)
    except Exception:
        logger.debug("Failed to record audit for line deletion")

    return line


def commission_line(db: Session, line_id: UUID, actor: dict | str | None = None):
    line = db.query(Line).filter(Line.id == line_id).first()

    if not line:
        raise NotFoundException(detail="Line not found")

    # Only lines in PROVISIONED state may be commissioned
    if not is_commissionable(line.status):
        raise BadRequestException(detail=f"Cannot commission line in status {line.status}")

    try:
        old = LineResponse.model_validate(line).model_dump()
    except Exception:
        old = None

    logger.info(f"Commissioning started for Line {line.id}")

    # Optional delay (simulate provisioning)
    time.sleep(2)

    # Transition to ACTIVE
    if not can_transition(line.status, LineStatus.ACTIVE):
        raise BadRequestException(
            detail=f"Invalid status transition during commission: {line.status} -> ACTIVE"
        )

    line.status = LineStatus.ACTIVE
    db.commit()
    db.refresh(line)

    logger.info(f"Commissioning completed for Line {line.id}")

    try:
        new = LineResponse.model_validate(line).model_dump()
        record_audit(db, actor, "commission_line", "line", str(line.id), old=old, new=new)
    except Exception:
        logger.debug("Failed to record audit for line commissioning")

    return line

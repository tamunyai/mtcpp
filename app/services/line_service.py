import time
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException, NotFoundException
from app.core.logging import get_logger
from app.core.state import can_transition, is_commissionable
from app.models.account import Account
from app.models.line import Line
from app.schemas.line import LineCreate, LineStatus

logger = get_logger()


def create_line(db: Session, account_id: UUID, line_data: LineCreate):
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
    return line


def get_lines_by_account(db: Session, account_id: UUID):
    return db.query(Line).filter(Line.account_id == account_id).all()


def update_line_status(db: Session, line_id: UUID, new_status: str):
    line = db.query(Line).filter(Line.id == line_id).first()

    if not line:
        raise NotFoundException(detail="Line not found")
    # Validate allowed state transition centrally
    if not can_transition(line.status, new_status):
        raise BadRequestException(
            detail=f"Invalid status transition: {line.status} -> {new_status}"
        )

    line.status = new_status
    db.commit()
    db.refresh(line)

    logger.info(f"Line status updated: Line {line.id} -> {new_status}")
    return line


def delete_line(db: Session, line_id: UUID):
    line = db.query(Line).filter(Line.id == line_id).first()

    if not line:
        raise NotFoundException(detail="Line not found")

    line.status = LineStatus.DELETED
    db.commit()

    logger.info(f"Line deleted: Line {line.id}")
    return line


def commission_line(db: Session, line_id: UUID):
    line = db.query(Line).filter(Line.id == line_id).first()

    if not line:
        raise NotFoundException(detail="Line not found")

    # Only lines in PROVISIONED state may be commissioned
    if not is_commissionable(line.status):
        raise BadRequestException(detail=f"Cannot commission line in status {line.status}")

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

    return line

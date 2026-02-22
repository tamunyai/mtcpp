import time

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException, NotFoundException
from app.core.logging import get_logger
from app.models.account import Account
from app.models.line import Line
from app.schemas.line import LineCreate, LineStatus

logger = get_logger()


def create_line(db: Session, account_id: int, line_data: LineCreate):
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


def get_lines_by_account(db: Session, account_id: int):
    return db.query(Line).filter(Line.account_id == account_id).all()


def update_line_status(db: Session, line_id: int, new_status: str):
    line = db.query(Line).filter(Line.id == line_id).first()

    if not line:
        raise NotFoundException(detail="Line not found")

    if line.status == LineStatus.DELETED:
        raise BadRequestException(detail="Cannot update a deleted line")

    if new_status == LineStatus.ACTIVE and line.status == LineStatus.DELETED:
        raise BadRequestException(detail="Cannot activate deleted line")

    line.status = new_status
    db.commit()
    db.refresh(line)

    logger.info(f"Line status updated: Line {line.id} -> {new_status}")
    return line


def delete_line(db: Session, line_id: int):
    line = db.query(Line).filter(Line.id == line_id).first()

    if not line:
        raise NotFoundException(detail="Line not found")

    line.status = LineStatus.DELETED
    db.commit()

    logger.info(f"Line deleted: Line {line.id}")
    return line


def commission_line(db: Session, line_id: int):
    line = db.query(Line).filter(Line.id == line_id).first()

    if not line:
        raise NotFoundException(detail="Line not found")

    # Validation rules
    if line.status == LineStatus.ACTIVE:
        raise BadRequestException(detail="Line is already active")

    if line.status == LineStatus.DELETED:
        raise BadRequestException(detail="Cannot commission deleted line")

    if line.status != LineStatus.PROVISIONED:
        raise BadRequestException(detail=f"Cannot commission line in status {line.status}")

    logger.info(f"Commissioning started for Line {line.id}")

    # Optional delay (simulate provisioning)
    time.sleep(2)

    line.status = LineStatus.ACTIVE
    db.commit()
    db.refresh(line)

    logger.info(f"Commissioning completed for Line {line.id}")

    return line

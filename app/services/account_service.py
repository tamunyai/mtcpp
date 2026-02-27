from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountResponse, AccountUpdate
from app.services.audit_service import record_audit

logger = get_logger()


def create_account(db: Session, account_data: AccountCreate, actor: dict | str | None = None):
    account = Account(
        full_name=account_data.full_name,
        email=account_data.email,
        phone=account_data.phone,
        status=account_data.status,
    )
    db.add(account)
    db.commit()
    db.refresh(account)

    logger.info(f"Account created: {account.id} ({account.email})")

    try:
        new = AccountResponse.model_validate(account).model_dump()
        record_audit(db, actor, "create_account", "account", str(account.id), old=None, new=new)
    except Exception:
        logger.debug("Failed to record audit for account creation")

    return account


def get_accounts(db: Session, limit: int = 100):
    return db.query(Account).limit(limit).all()


def get_account_by_id(db: Session, account_id: UUID):
    account = db.query(Account).filter(Account.id == account_id).first()

    if not account:
        raise NotFoundException(detail="Account not found")

    return account


def update_account(
    db: Session, account_id: UUID, account_data: AccountUpdate, actor: dict | str | None = None
):
    account = get_account_by_id(db, account_id)

    try:
        old = AccountResponse.model_validate(account).model_dump()
    except Exception:
        old = None

    for field, value in account_data.model_dump(exclude_unset=True).items():
        setattr(account, field, value)

    db.commit()
    db.refresh(account)

    logger.info(f"Account updated: {account.id}")

    try:
        new = AccountResponse.model_validate(account).model_dump()
        record_audit(db, actor, "update_account", "account", str(account.id), old=old, new=new)
    except Exception:
        logger.debug("Failed to record audit for account update")

    return account

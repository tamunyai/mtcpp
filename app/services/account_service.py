from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountUpdate

logger = get_logger()


def create_account(db: Session, account_data: AccountCreate):
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
    return account


def get_accounts(db: Session):
    return db.query(Account).all()


def get_account_by_id(db: Session, account_id: int):
    account = db.query(Account).filter(Account.id == account_id).first()

    if not account:
        raise NotFoundException(detail="Account not found")

    return account


def update_account(db: Session, account_id: int, account_data: AccountUpdate):
    account = get_account_by_id(db, account_id)

    for field, value in account_data.model_dump(exclude_unset=True).items():
        setattr(account, field, value)

    db.commit()
    db.refresh(account)

    logger.info(f"Account updated: {account.id}")
    return account

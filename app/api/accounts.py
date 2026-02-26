from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_role
from app.db.session import get_db
from app.schemas.account import AccountCreate, AccountResponse, AccountUpdate
from app.schemas.user import UserRole
from app.services.account_service import (
    create_account,
    get_account_by_id,
    get_accounts,
    update_account,
)

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("/", response_model=AccountResponse)
def create_new_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.ADMIN)),
):
    created = create_account(db, account, actor=user)
    return AccountResponse.model_validate(created)


@router.get("/", response_model=List[AccountResponse])
def list_accounts(db: Session = Depends(get_db), user=Depends(get_current_user)):
    accounts = get_accounts(db)
    return [AccountResponse.model_validate(a) for a in accounts]


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(account_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    account = get_account_by_id(db, account_id)
    return AccountResponse.model_validate(account)


@router.put("/{account_id}", response_model=AccountResponse)
def update_existing_account(
    account_id: UUID,
    account: AccountUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.ADMIN)),
):
    updated = update_account(db, account_id, account, actor=user)
    return AccountResponse.model_validate(updated)

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_role
from app.db.session import get_db
from app.schemas.line import LineCreate, LineResponse, LineUpdateStatus
from app.schemas.user import UserRole
from app.services.line_service import (
    commission_line,
    create_line,
    delete_line,
    get_lines_by_account,
    update_line_status,
)

router = APIRouter(tags=["Lines"])


@router.post("/accounts/{account_id}/lines", response_model=LineResponse)
def create_new_line(
    account_id: UUID,
    line: LineCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.ADMIN)),
):
    return create_line(db, account_id, line)


@router.get("/accounts/{account_id}/lines", response_model=List[LineResponse])
def list_lines_for_account(
    account_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    return get_lines_by_account(db, account_id)


@router.patch("/lines/{line_id}/status", response_model=LineResponse)
def change_line_status(
    line_id: UUID,
    status_update: LineUpdateStatus,
    db: Session = Depends(get_db),
    user=Depends(require_role(UserRole.ADMIN)),
):
    return update_line_status(db, line_id, status_update.status)


@router.delete("/lines/{line_id}", response_model=LineResponse)
def remove_line(
    line_id: UUID, db: Session = Depends(get_db), user=Depends(require_role(UserRole.ADMIN))
):
    return delete_line(db, line_id)


@router.post("/lines/{line_id}/commission", response_model=LineResponse)
def commission_line_endpoint(
    line_id: UUID, db: Session = Depends(get_db), user=Depends(require_role(UserRole.ADMIN))
):
    return commission_line(db, line_id)

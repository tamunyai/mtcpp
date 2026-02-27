import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import get_logger
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.account import Account, AccountStatus
from app.models.user import User
from app.schemas.account import AccountCreate
from app.schemas.line import LineCreate
from app.schemas.user import UserRole
from app.services.account_service import create_account
from app.services.line_service import create_line

SAMPLE_FILE = Path(settings.BASE_DIR) / "data" / "sample_data.json"

logger = get_logger()


def _load_sample_data(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode sample data JSON at {path}: {e}")
        return None


def _seed_users(db: Session, users: List[Dict[str, Any]]) -> None:
    for u in users:
        username = u.get("username")
        if not username:
            continue

        exists = db.query(User).filter(User.username == username).first()
        if not exists:
            user = User(
                username=username,
                password_hash=hash_password(u.get("password", "password")),
                role=UserRole(u.get("role", "OPERATOR")),
            )
            db.add(user)
            logger.info(f"User created: {username}")


def _seed_accounts_and_lines(db: Session, accounts: List[Dict[str, Any]]) -> None:
    for acc in accounts:
        try:
            acc_payload = AccountCreate(
                full_name=acc["full_name"],
                email=acc["email"],
                phone=acc["phone"],
                status=acc.get("status", AccountStatus.ACTIVE),
            )

        except KeyError as e:
            logger.error(f"Missing required account field: {e}")
            continue

        account = db.query(Account).filter(Account.email == acc_payload.email).first()

        if not account:
            try:
                account = create_account(db, acc_payload, actor="seed-script")
                db.commit()
                logger.info(f"Created account: {account.email}")

            except Exception as e:
                db.rollback()
                logger.error(f"Failed to create account {acc_payload.email}: {e}")
                continue

        # Seed Lines
        for line in acc.get("lines", []):
            try:
                line_payload = LineCreate(msisdn=line["msisdn"], plan_name=line["plan_name"])
                created = create_line(db, account.id, line_payload, actor="seed-script")
                db.commit()
                logger.info(f"  Created line: {created.msisdn}")

            except (AppException, IntegrityError):
                db.rollback()

            except Exception as e:
                db.rollback()
                logger.error(f"  Failed to create line {line.get('msisdn')}: {e}")


def init_db() -> int:
    data = _load_sample_data(SAMPLE_FILE)
    if not data:
        logger.error(f"Sample data file not found or empty: {SAMPLE_FILE}")

    db = SessionLocal()
    try:
        _seed_users(db, data.get("users", []))  # type: ignore
        _seed_accounts_and_lines(db, data.get("accounts", []))  # type: ignore
        db.commit()

    except Exception as e:
        logger.error(f"An unexpected error occurred during database initialization: {e}")
        db.rollback()

    finally:
        db.close()

    return 0


if __name__ == "__main__":
    init_db()

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.user import UserRole


def init_db():
    db: Session = SessionLocal()

    try:
        if not db.query(User).first():
            admin = User(
                username="admin",
                password_hash=hash_password("admin123"),
                role=UserRole.ADMIN,
            )
            operator = User(
                username="operator",
                password_hash=hash_password("operator123"),
                role=UserRole.OPERATOR,
            )

            db.add(admin)
            db.add(operator)
            db.commit()
            print("Seeded users")

    finally:
        db.close()


if __name__ == "__main__":
    init_db()

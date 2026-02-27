import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User
from app.schemas.user import UserRole

# Use in-memory DB for speed
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def init_db():
    Base.metadata.create_all(bind=engine)
    db: Session = TestingSessionLocal()

    try:
        admin = User(
            username="admin_test", password_hash=hash_password("admin123"), role=UserRole.ADMIN
        )
        operator = User(
            username="operator_test",
            password_hash=hash_password("operator123"),
            role=UserRole.OPERATOR,
        )

        db.add(admin)
        db.add(operator)
        db.commit()

    finally:
        db.close()

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()

    session = TestingSessionLocal(bind=connection)
    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

    # Clean up overrides after test
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token(client):
    response = client.post("/auth/login", json={"username": "admin_test", "password": "admin123"})
    return response.json()["access_token"]


@pytest.fixture
def operator_token(client):
    response = client.post(
        "/auth/login", json={"username": "operator_test", "password": "operator123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def admin_client(admin_token):
    with TestClient(app) as c:
        c.headers.update({"Authorization": f"Bearer {admin_token}"})
        yield c


@pytest.fixture
def operator_client(operator_token):
    with TestClient(app) as c:
        c.headers.update({"Authorization": f"Bearer {operator_token}"})
        yield c

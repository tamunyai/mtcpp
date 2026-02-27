import os

from pydantic import computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Mini Telecom Commissioning & Provisioning Platform - API"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = (
        "A lightweight service provisioning & commissioning API for accounts and service lines."
    )
    DEBUG: bool = False
    PROD: bool = False

    # Security & JWT
    SECRET_KEY: str = "super-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 24 * 60  # 1 day

    # Pydantic Configuration
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",  # Prevents crashing if extra vars are in .env
    }

    # Paths
    @computed_field
    @property
    def BASE_DIR(self) -> str:
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Database & Logs
    @computed_field
    @property
    def DB_PATH(self) -> str:
        return os.path.join(self.BASE_DIR, "data", "application.db")

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"sqlite:///{self.DB_PATH}"

    @computed_field
    @property
    def LOG_DIR(self) -> str:
        return os.path.join(self.BASE_DIR, "logs")

    @computed_field
    @property
    def LOG_FILE(self) -> str:
        return os.path.join(self.LOG_DIR, "{time:YYYY-MM-DD}.log")

    @computed_field
    @property
    def DEV(self) -> bool:
        return not self.PROD


settings = Settings()

# Ensure the directories exist on startup
os.makedirs(os.path.dirname(settings.DB_PATH), exist_ok=True)
os.makedirs(settings.LOG_DIR, exist_ok=True)

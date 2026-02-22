import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Mini Telecom Commissioning & Provisioning Platform"
    DEBUG: bool = False

    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Database & Logs
    DB_PATH: str = os.path.join(BASE_DIR, "data", "application.db")
    DATABASE_URL: str = f"sqlite:///{DB_PATH}"
    LOG_DIR: str = os.path.join(BASE_DIR, "logs")
    LOG_FILE: str = os.path.join(LOG_DIR, "{time:YYYY-MM-DD}.log")

    # Security & JWT
    SECRET_KEY: str = "super-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Pydantic Configuration
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Prevents crashing if extra vars are in .env


settings = Settings()

# Ensure the directories exist on startup
os.makedirs(os.path.dirname(settings.DB_PATH), exist_ok=True)
os.makedirs(settings.LOG_DIR, exist_ok=True)

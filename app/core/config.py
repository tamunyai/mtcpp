import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    # App Settings
    APP_NAME: str = os.getenv("APP_NAME", "Mini Telecom Commissioning & Provisioning Platform")
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    # Security & JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30


settings = Settings()

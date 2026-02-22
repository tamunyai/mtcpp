from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger()

app = FastAPI(title=settings.APP_NAME)


@app.get("/")
def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok"}

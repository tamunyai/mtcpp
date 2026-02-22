from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import accounts, auth, lines
from app.core.config import settings
from app.core.logging import get_logger
from app.db.base import Base
from app.db.init_db import init_db
from app.db.session import engine

logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")

    try:
        Base.metadata.create_all(bind=engine)
        init_db()  # Seed Admin/Operator users

        logger.info("Database initialized and seeded successfully.")

    except Exception as e:
        logger.error(f"Error during database initialization: {e}")

    yield  # The app stays here while running
    logger.info("Shutting down backend services...")


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=400,
        content={"error": "Validation Error", "details": exc.errors()},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "message": "Something went wrong"},
    )


app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(lines.router)


@app.get("/")
def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok"}

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api import accounts, auth, lines
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import get_logger, setup_logging
from app.db.base import Base
from app.db.init_db import init_db
from app.db.session import SessionLocal, engine

logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Initializing database...")

    try:
        Base.metadata.create_all(bind=engine)
        init_db()  # Seed Admin/Operator users

        logger.info("Database initialized and seeded successfully.")

    except Exception as e:
        logger.error(f"Error during database initialization: {e}")

    yield  # The app stays here while running
    logger.info("Shutting down backend services...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan,
    debug=settings.DEBUG,
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.__class__.__name__, "message": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error at {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"error": "Validation Error", "details": exc.errors()},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception occurred")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal Server Error", "message": "An unexpected error occurred"},
    )


app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(lines.router)


@app.get("/", tags=["System"])
def root():
    return {"app": settings.APP_NAME, "version": "0.1.0", "docs": "/docs", "status": "running"}


@app.get("/health", tags=["System"])
def health_check():
    health_status = {"status": "healthy", "database": "connected"}

    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        health_status["status"] = "unhealthy"
        health_status["database"] = "disconnected"

        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=health_status)

    return health_status

import logging
import tomllib
from contextlib import asynccontextmanager
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI

from app import crud
from app.config import settings
from app.database import close_engine, create_db_and_tables
from app.logging import setup_logging
from app.models import feed_tables_for_dev
from app.routers import user_router

# configure logger
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    if settings.is_dev():
        await feed_tables_for_dev()
    yield
    await close_engine()


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)


@lru_cache(maxsize=1)
def _load_version() -> str:
    """Read project version from pyproject.toml (cached)."""
    pyproject_path = Path(__file__).parent / "pyproject.toml"

    with pyproject_path.open("rb") as f:
        data = tomllib.load(f)

    return data["project"]["version"]


@app.get("/")
async def root():
    """Root endpoint with metadata for quick inspection."""
    logger.debug("Entering root endpoint")

    try:
        app_version = _load_version()
        message = "ok"
    except Exception as e:
        app_version = "0.0.0"
        logger.error(f"{e}")
        message = str(e)

    return {
        "name": "API birthday",
        "version": app_version,
        "message": message,
        "environment": settings.app_env,
        "docs": "/docs",
        "openapi": "/openapi.json",
    }

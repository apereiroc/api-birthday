from fastapi import FastAPI
from pathlib import Path
import tomllib
from app.logging import setup_logging
from app.config import settings
import logging
from app.database import SessionDep, create_db_and_tables, feed_tables_for_dev
from contextlib import asynccontextmanager
from app.routers import user_router
from app import crud


# configure logger
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    if settings.is_dev():
        await feed_tables_for_dev()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)


async def _load_version() -> str:
    """Read project version from pyproject.toml."""
    pyproject_path = Path(__file__).parent / "pyproject.toml"

    logger.debug(f"Trying to open pyproject from {pyproject_path}")
    with pyproject_path.open("rb") as f:
        data = tomllib.load(f)
    logger.debug(f"Read data: {data}")

    project_data = data["project"]
    version = project_data["version"]

    return version


@app.get("/")
async def root():
    """Root endpoint with metadata for quick inspection."""
    logger.debug("Entering root endpoint")

    try:
        app_version = await _load_version()
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

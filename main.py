from fastapi import FastAPI
from pathlib import Path
import tomllib
from app.logging import setup_logging
from app.config import settings
import logging
from app.database import SessionDep, create_db_and_tables
from contextlib import asynccontextmanager


# configure logger
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


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
async def root(session: SessionDep):
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

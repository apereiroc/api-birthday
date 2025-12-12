from app.config import Environment, settings
from sqlmodel import Session, SQLModel, create_engine
from typing import Annotated
from fastapi import Depends
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = settings.database_url

kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    # for sqlite, add check_same_thread=False to allow multi-threaded access in dev/test
    kwargs["connect_args"] = {"check_same_thread": False}

# only print DB transactions in development
# this might be eventually removed...
is_dev: bool = settings.app_env is Environment.development
engine = create_engine(DATABASE_URL, echo=is_dev, **kwargs)


async def create_db_and_tables():
    logger.debug("Creating db and tables..")
    SQLModel.metadata.create_all(engine)


async def get_db():
    """Dependency to get a database session for each request"""
    with Session(engine) as session:
        yield session


# this session dependency can be injected into the endpoints
SessionDep = Annotated[Session, Depends(get_db)]

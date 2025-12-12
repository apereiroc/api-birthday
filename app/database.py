from app.config import settings
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

engine = create_engine(DATABASE_URL, echo=True, **kwargs)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_db():
    """Dependency to get a database session for each request."""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]

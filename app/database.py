from app.config import settings
from sqlmodel import Session, SQLModel, create_engine, select
from typing import Annotated
from fastapi import Depends
import logging
from app.models import User
from faker import Faker

logger = logging.getLogger(__name__)

DATABASE_URL = settings.database_url

kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    # for sqlite, add check_same_thread=False to allow multi-threaded access in dev/test
    kwargs["connect_args"] = {"check_same_thread": False}

# only print DB transactions in development
# this might be eventually removed...
is_dev: bool = settings.is_dev()
engine = create_engine(DATABASE_URL, echo=is_dev, **kwargs)


async def create_db_and_tables():
    logger.debug("Creating db and tables ...")
    SQLModel.metadata.create_all(engine)


async def feed_tables_for_dev():
    logger.debug("Feeding tables ...")
    with Session(engine) as session:
        faker = Faker()
        for i in range(10):
            result = session.exec(select(User).where(User.telegram_id == i)).first()
            logger.debug(f"Got result: {result}")
            if result is None:
                u = User(
                    telegram_id=i,
                    first_name=faker.first_name(),
                    last_name=faker.last_name(),
                    username=faker.user_name(),
                )
                session.add(u)
        session.commit()


async def get_db():
    """Dependency to get a database session for each request"""
    with Session(engine) as session:
        yield session


# this session dependency can be injected into the endpoints
SessionDep = Annotated[Session, Depends(get_db)]

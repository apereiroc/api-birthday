import logging
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

logger = logging.getLogger(__name__)

DATABASE_URL = settings.database_url

kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    # for sqlite, add check_same_thread=False to allow multi-threaded access in dev/test
    kwargs["connect_args"] = {"check_same_thread": False}

# only print DB transactions in development
# this might be eventually removed...
is_dev: bool = settings.is_dev()
engine = create_async_engine(
    DATABASE_URL,
    echo=is_dev,
    pool_pre_ping=True,
    **kwargs,
)
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# create base model for tables
class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def close_engine() -> None:
    logger.info("Disposing database engine")
    await engine.dispose()


# this session dependency can be injected into the endpoints
SessionDep = Annotated[AsyncSession, Depends(get_db)]


# utility to create database and tables
async def create_db_and_tables():
    logger.debug("Creating db and tables ...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

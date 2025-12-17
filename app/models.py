import logging
from datetime import datetime
from faker import Faker
from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base, async_session

logger = logging.getLogger(__name__)


"""
User models
    Users are actual app users, who perform CRUD operations via the API
"""


# class User(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     telegram_id: int = Field(unique=True, index=True)
#     first_name: str
#     last_name: str | None = None
#     username: str | None = None
#     created_at: datetime = Field(default_factory=datetime.now)

# persons: list["Person"] = Relationship(back_populates="user", cascade_delete=True)


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True, index=True, nullable=False)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str | None] = mapped_column(default=None, nullable=True)
    username: Mapped[str | None] = mapped_column(default=None, nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class UserBase(PydanticBaseModel):
    first_name: str
    last_name: str | None = None
    username: str | None = None


class UserPublic(UserBase):
    id: int
    created_at: datetime


class UserCreate(UserBase):
    telegram_id: int


class UserUpdate(PydanticBaseModel):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None


# utility to insert some data in the tables
async def feed_tables_for_dev():
    logger.debug("Feeding tables ...")
    async with async_session() as session:
        faker = Faker()
        # insert some users
        for i in range(10):
            result = (
                (await session.execute(select(User).where(User.telegram_id == i)))
                .scalars()
                .first()
            )
            logger.debug(f"Got result: {result}")
            if result is None:
                u = User(
                    telegram_id=i,
                    first_name=faker.first_name(),
                    last_name=faker.last_name(),
                    username=faker.user_name(),
                )
                session.add(u)
        await session.commit()


# """
# Person models
#     A person is the one referred to in a specific birthday
#     Relationship comments can be added
# """
#
#
# class Person(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     user_id: int | None = Field(default=None, foreign_key="user.id")
#     name: str
#     last_name: str
#     relationship_type: str | None = Field(
#         default=None,
#         description="Kind of relationship, e.g. friend, mother, colleague from job #4, etc.",
#     )
#
#     user: User | None = Relationship(back_populates="persons")
#     birthdays: list["Birthday"] = Relationship(
#         back_populates="person", cascade_delete=True
#     )
#
#
# """
# Birthday models
#     A birthday date is the central element in this application
#     Note that the year of birth is optional
# """
#
#
# class Birthday(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     person_id: int | None = Field(default=None, foreign_key="person.id")
#     day: int = Field(ge=1, le=31)
#     month: int = Field(ge=1, le=12)
#     year: int | None = Field(default=None, gt=1900)
#
#     person: Person | None = Relationship(back_populates="birthdays")

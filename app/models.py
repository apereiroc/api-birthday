from sqlmodel import SQLModel, Field
from datetime import datetime


"""
User models
    Users are actual app users, who perform CRUD operations via the API
"""


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    telegram_id: int = Field(unique=True, index=True)
    first_name: str
    last_name: str | None = None
    username: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)

    # persons: list["Person"] = Relationship(back_populates="user", cascade_delete=True)


class UserBase(SQLModel):
    first_name: str
    last_name: str | None = None
    username: str | None = None


class UserPublic(UserBase):
    id: int
    created_at: datetime


class UserCreate(UserBase):
    telegram_id: int


class UserUpdate(SQLModel):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None


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

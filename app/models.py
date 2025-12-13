from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    api_key: str = Field(unique=True, index=True, nullable=False)

    persons: list["Person"] = Relationship(back_populates="user", cascade_delete=True)


class Person(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id")
    name: str
    last_name: str
    relationship_type: str | None = Field(
        default=None,
        description="Kind of relationship, e.g. friend, mother, colleague from job #4, etc.",
    )

    user: User | None = Relationship(back_populates="persons")
    birthdays: list["Birthday"] = Relationship(
        back_populates="person", cascade_delete=True
    )


class Birthday(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    person_id: int | None = Field(default=None, foreign_key="person.id")
    day: int = Field(ge=1, le=31)
    month: int = Field(ge=1, le=12)
    year: int | None = Field(default=None, gt=1900)

    person: Person | None = Relationship(back_populates="birthdays")

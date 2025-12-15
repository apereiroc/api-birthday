import pytest
from fastapi import HTTPException
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from app.models import User, UserCreate, UserPublic
from app.crud import create_user_if_not_exists
from app.database import get_db


@pytest.fixture(name="session")
def session_fixture():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.mark.anyio
async def test_create_user_success(session: Session):
    """Test creating a new user successfully."""
    user_data = UserCreate(
        telegram_id=123456789,
        first_name="John",
        last_name="Doe",
        username="johndoe",
    )

    result = await create_user_if_not_exists(user_data, session)

    assert result.telegram_id == 123456789
    assert result.first_name == "John"
    assert result.last_name == "Doe"
    assert result.username == "johndoe"
    assert result.id is not None
    assert result.created_at is not None


@pytest.mark.anyio
async def test_create_user_minimal_data(session: Session):
    """Test creating a user with minimal required fields."""
    user_data = UserCreate(
        telegram_id=987654321,
        first_name="Jane",
    )

    result = await create_user_if_not_exists(user_data, session)

    assert result.telegram_id == 987654321
    assert result.first_name == "Jane"
    assert result.last_name is None
    assert result.username is None
    assert result.id is not None


@pytest.mark.anyio
async def test_create_user_duplicate_telegram_id(session: Session):
    """Test that creating a user with duplicate telegram_id raises HTTPException."""
    user_data = UserCreate(
        telegram_id=111222333,
        first_name="Alice",
        last_name="Smith",
    )

    # Create first user
    await create_user_if_not_exists(user_data, session)

    # Try to create duplicate
    duplicate_data = UserCreate(
        telegram_id=111222333,  # Same telegram_id
        first_name="Bob",
        last_name="Jones",
    )

    with pytest.raises(HTTPException) as exc_info:
        await create_user_if_not_exists(duplicate_data, session)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "User already exists"


@pytest.mark.anyio
async def test_create_multiple_users(session: Session):
    """Test creating multiple users with different telegram_ids."""
    users_data = [
        UserCreate(telegram_id=111, first_name="User1"),
        UserCreate(telegram_id=222, first_name="User2"),
        UserCreate(telegram_id=333, first_name="User3"),
    ]

    results = []
    for user_data in users_data:
        result = await create_user_if_not_exists(user_data, session)
        results.append(result)

    assert len(results) == 3
    assert results[0].telegram_id == 111
    assert results[1].telegram_id == 222
    assert results[2].telegram_id == 333

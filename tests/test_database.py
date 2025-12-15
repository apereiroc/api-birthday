import pytest
from sqlmodel import Session, create_engine, SQLModel, select
from sqlmodel.pool import StaticPool
from app.models import User
from app.database import get_db


@pytest.fixture(name="engine")
def engine_fixture():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine):
    """Create a database session for testing."""
    with Session(engine) as session:
        yield session


def test_create_user_in_db(session: Session):
    """Test creating a user in the database."""
    user = User(
        telegram_id=123456789,
        first_name="John",
        last_name="Doe",
        username="johndoe",
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    assert user.id is not None
    assert user.telegram_id == 123456789
    assert user.first_name == "John"


def test_query_user_by_telegram_id(session: Session):
    """Test querying a user by telegram_id."""
    user = User(
        telegram_id=987654321,
        first_name="Jane",
    )
    session.add(user)
    session.commit()

    # Query by telegram_id
    result = session.exec(
        select(User).where(User.telegram_id == 987654321)
    ).first()

    assert result is not None
    assert result.telegram_id == 987654321
    assert result.first_name == "Jane"


def test_query_nonexistent_user(session: Session):
    """Test querying a user that doesn't exist."""
    result = session.exec(
        select(User).where(User.telegram_id == 999999999)
    ).first()

    assert result is None


def test_update_user(session: Session):
    """Test updating a user in the database."""
    user = User(telegram_id=111222333, first_name="Old")
    session.add(user)
    session.commit()
    session.refresh(user)

    # Update
    user.first_name = "New"
    user.last_name = "Name"
    session.add(user)
    session.commit()
    session.refresh(user)

    assert user.first_name == "New"
    assert user.last_name == "Name"


def test_delete_user(session: Session):
    """Test deleting a user from the database."""
    user = User(telegram_id=444555666, first_name="ToDelete")
    session.add(user)
    session.commit()
    user_id = user.id

    # Delete
    session.delete(user)
    session.commit()

    # Verify deletion
    result = session.get(User, user_id)
    assert result is None


def test_unique_telegram_id_constraint(session: Session):
    """Test that telegram_id unique constraint is enforced."""
    user1 = User(telegram_id=123, first_name="User1")
    session.add(user1)
    session.commit()

    user2 = User(telegram_id=123, first_name="User2")
    session.add(user2)

    with pytest.raises(Exception):  # IntegrityError
        session.commit()


@pytest.mark.anyio
async def test_get_db_generator():
    """Test that get_db yields a session asynchronously."""
    generator = get_db()
    session = await anext(generator)

    assert isinstance(session, Session)

    await generator.aclose()
    with pytest.raises(StopAsyncIteration):
        await anext(generator)


def test_query_all_users(session: Session):
    """Test querying all users."""
    users = [
        User(telegram_id=111, first_name="User1"),
        User(telegram_id=222, first_name="User2"),
        User(telegram_id=333, first_name="User3"),
    ]

    for user in users:
        session.add(user)
    session.commit()

    # Query all
    results = session.exec(select(User)).all()

    assert len(results) >= 3
    telegram_ids = [user.telegram_id for user in results]
    assert 111 in telegram_ids
    assert 222 in telegram_ids
    assert 333 in telegram_ids


def test_user_created_at_auto_populated(session: Session):
    """Test that created_at is automatically set."""
    user = User(telegram_id=777888999, first_name="Test")
    session.add(user)
    session.commit()
    session.refresh(user)

    assert user.created_at is not None
    from datetime import datetime

    assert isinstance(user.created_at, datetime)

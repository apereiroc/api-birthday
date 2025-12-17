import pytest
from app.models import User
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession


from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


@pytest.mark.anyio
async def test_create_user_in_db(session: AsyncSession):
    """Test creating a user in the database."""
    user = User(
        telegram_id=123456789,
        first_name="John",
        last_name="Doe",
        username="johndoe",
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    assert user.id is not None
    assert user.telegram_id == 123456789
    assert user.first_name == "John"


@pytest.mark.anyio
async def test_query_user_by_telegram_id(session: AsyncSession):
    """Test querying a user by telegram_id."""
    user = User(
        telegram_id=987654321,
        first_name="Jane",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Query by telegram_id
    result = await session.execute(select(User).where(User.telegram_id == 987654321))
    user_result = result.scalar_one_or_none()

    assert user_result is not None
    assert user_result.telegram_id == 987654321
    assert user_result.first_name == "Jane"


@pytest.mark.anyio
async def test_query_nonexistent_user(session: AsyncSession):
    """Test querying a user that doesn't exist."""
    result = await session.execute(select(User).where(User.telegram_id == 999999999))
    user_result = result.scalar_one_or_none()

    assert user_result is None


@pytest.mark.anyio
async def test_update_user(session: AsyncSession):
    """Test updating a user in the database."""
    user = User(telegram_id=111222333, first_name="Old")
    session.add(user)
    await session.commit()
    await session.refresh(user)

    # Update
    user.first_name = "New"
    user.last_name = "Name"
    session.add(user)
    await session.commit()
    await session.refresh(user)

    assert user.first_name == "New"
    assert user.last_name == "Name"


@pytest.mark.anyio
async def test_delete_user(session: AsyncSession):
    """Test deleting a user from the database."""
    user = User(telegram_id=444555666, first_name="ToDelete")
    session.add(user)
    await session.commit()
    await session.refresh(user)
    user_id = user.id

    # Delete
    await session.delete(user)
    await session.commit()

    # Verify deletion
    result = await session.get(User, user_id)
    assert result is None


@pytest.mark.anyio
async def test_unique_telegram_id_constraint(session: AsyncSession):
    """Test that telegram_id unique constraint is enforced."""
    user1 = User(telegram_id=123, first_name="User1")
    session.add(user1)
    await session.commit()

    user2 = User(telegram_id=123, first_name="User2")
    session.add(user2)

    with pytest.raises(IntegrityError):
        await session.commit()


@pytest.mark.anyio
async def test_get_db_generator():
    """Test that get_db yields a session asynchronously."""
    generator = get_db()
    session = await anext(generator)

    from sqlalchemy.ext.asyncio import AsyncSession

    assert isinstance(session, AsyncSession)

    await generator.aclose()
    with pytest.raises(StopAsyncIteration):
        await anext(generator)


@pytest.mark.anyio
async def test_query_all_users(session: AsyncSession):
    """Test querying all users."""
    users = [
        User(telegram_id=111, first_name="User1"),
        User(telegram_id=222, first_name="User2"),
        User(telegram_id=333, first_name="User3"),
    ]

    session.add_all(users)
    await session.commit()

    result = await session.execute(select(User))
    all_users = result.scalars().all()

    assert len(all_users) >= 3
    telegram_ids = [u.telegram_id for u in all_users]
    assert 111 in telegram_ids
    assert 222 in telegram_ids
    assert 333 in telegram_ids


@pytest.mark.anyio
async def test_user_created_at_auto_populated(session: AsyncSession):
    """Test that created_at is automatically set."""
    from datetime import datetime

    user = User(telegram_id=777888999, first_name="Test")
    session.add(user)
    await session.commit()
    await session.refresh(user)

    assert user.created_at is not None
    assert isinstance(user.created_at, datetime)

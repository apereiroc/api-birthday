import pytest
from datetime import datetime
from pydantic import ValidationError
from app.models import User, UserBase, UserCreate, UserPublic, UserUpdate


def test_user_model_complete():
    """Test User model with all fields."""
    now = datetime.now()
    user = User(
        id=1,
        telegram_id=123456789,
        first_name="John",
        last_name="Doe",
        username="johndoe",
        created_at=now,
    )

    assert user.id == 1
    assert user.telegram_id == 123456789
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.username == "johndoe"
    assert user.created_at == now


def test_user_model_minimal():
    """Test User model with minimal required fields."""
    user = User(
        telegram_id=987654321,
        first_name="Jane",
    )

    assert user.id is None  # Not set yet
    assert user.telegram_id == 987654321
    assert user.first_name == "Jane"
    assert user.last_name is None
    assert user.username is None
    assert isinstance(user.created_at, datetime)


def test_user_base_model():
    """Test UserBase model."""
    user_base = UserBase(
        first_name="Alice",
        last_name="Smith",
        username="alicesmith",
    )

    assert user_base.first_name == "Alice"
    assert user_base.last_name == "Smith"
    assert user_base.username == "alicesmith"


def test_user_create_model():
    """Test UserCreate model."""
    user_create = UserCreate(
        telegram_id=555666777,
        first_name="Bob",
        last_name="Johnson",
        username="bjohnson",
    )

    assert user_create.telegram_id == 555666777
    assert user_create.first_name == "Bob"
    assert user_create.last_name == "Johnson"
    assert user_create.username == "bjohnson"


def test_user_create_missing_telegram_id():
    """Test that UserCreate requires telegram_id."""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(first_name="Test")

    errors = exc_info.value.errors()
    assert any(error["loc"] == ("telegram_id",) for error in errors)


def test_user_public_model():
    """Test UserPublic model."""
    now = datetime.now()
    user_public = UserPublic(
        id=10,
        first_name="Charlie",
        last_name="Brown",
        username="cbrown",
        created_at=now,
    )

    assert user_public.id == 10
    assert user_public.first_name == "Charlie"
    assert user_public.last_name == "Brown"
    assert user_public.username == "cbrown"
    assert user_public.created_at == now


def test_user_update_model_all_fields():
    """Test UserUpdate model with all fields."""
    user_update = UserUpdate(
        first_name="Updated",
        last_name="Name",
        username="updated_username",
    )

    assert user_update.first_name == "Updated"
    assert user_update.last_name == "Name"
    assert user_update.username == "updated_username"


def test_user_update_model_partial():
    """Test UserUpdate model with partial fields."""
    user_update = UserUpdate(first_name="NewName")

    assert user_update.first_name == "NewName"
    assert user_update.last_name is None
    assert user_update.username is None


def test_user_update_model_empty():
    """Test UserUpdate model with no fields (all optional)."""
    user_update = UserUpdate()

    assert user_update.first_name is None
    assert user_update.last_name is None
    assert user_update.username is None


def test_user_model_dump():
    """Test that User can be dumped to dict."""
    user = User(
        telegram_id=111222333,
        first_name="Test",
        last_name="User",
    )

    user_dict = user.model_dump()

    assert user_dict["telegram_id"] == 111222333
    assert user_dict["first_name"] == "Test"
    assert user_dict["last_name"] == "User"
    assert "created_at" in user_dict

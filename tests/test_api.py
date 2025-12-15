import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from app.database import get_db
from main import app


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


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with database override."""

    def get_session_override():
        return session

    app.dependency_overrides[get_db] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_root_endpoint(client: TestClient):
    """Test the root endpoint returns metadata."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "message" in data
    assert "environment" in data
    assert "docs" in data
    assert "openapi" in data

    assert data["name"] == "API birthday"
    assert data["docs"] == "/docs"
    assert data["openapi"] == "/openapi.json"


def test_create_user_endpoint(client: TestClient):
    """Test creating a user through the API."""
    user_data = {
        "telegram_id": 123456789,
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe",
    }

    response = client.post("/users/", json=user_data)
    assert response.status_code == 200

    data = response.json()
    assert "telegram_id" not in data  # not exposed publicly
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["username"] == "johndoe"
    assert "id" in data
    assert "created_at" in data


def test_create_user_minimal(client: TestClient):
    """Test creating a user with minimal data."""
    user_data = {
        "telegram_id": 987654321,
        "first_name": "Jane",
    }

    response = client.post("/users/", json=user_data)
    assert response.status_code == 200

    data = response.json()
    assert "telegram_id" not in data
    assert data["first_name"] == "Jane"
    assert data["last_name"] is None
    assert data["username"] is None


def test_create_user_duplicate(client: TestClient):
    """Test that creating duplicate user returns 409."""
    user_data = {
        "telegram_id": 111222333,
        "first_name": "Alice",
    }

    # Create first user
    response1 = client.post("/users/", json=user_data)
    assert response1.status_code == 200

    # Try to create duplicate
    response2 = client.post("/users/", json=user_data)
    assert response2.status_code == 409
    assert response2.json()["detail"] == "User already exists"


def test_create_user_invalid_data(client: TestClient):
    """Test creating user with invalid data returns 422."""
    user_data = {
        "first_name": "Bob",
        # Missing required telegram_id
    }

    response = client.post("/users/", json=user_data)
    assert response.status_code == 422


def test_create_user_invalid_telegram_id_type(client: TestClient):
    """Test creating user with wrong telegram_id type."""
    user_data = {
        "telegram_id": "not_an_integer",
        "first_name": "Bob",
    }

    response = client.post("/users/", json=user_data)
    assert response.status_code == 422


def test_openapi_endpoint(client: TestClient):
    """Test that OpenAPI schema is accessible."""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data


def test_docs_endpoint(client: TestClient):
    """Test that /docs is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_create_multiple_users(client: TestClient):
    """Test creating multiple users."""
    users = [
        {"telegram_id": 111, "first_name": "User1"},
        {"telegram_id": 222, "first_name": "User2"},
        {"telegram_id": 333, "first_name": "User3"},
    ]

    for user_data in users:
        response = client.post("/users/", json=user_data)
        assert response.status_code == 200
        assert "telegram_id" not in response.json()

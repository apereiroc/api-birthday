from app.config import Settings, Environment
from pytest import MonkeyPatch
import pathlib


def test_settings_defaults_tmp_env(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch):
    """Defaults load when no env vars are set."""

    # Ensure env vars are unset
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    # Change to tmp_path to avoid loading project .env
    monkeypatch.chdir(tmp_path)

    settings = Settings()

    assert settings.app_env == Environment.development
    assert settings.log_level == "INFO"
    assert settings.database_url == "sqlite://"


def test_settings_env_overrides(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch):
    """Environment variables override defaults."""

    # Set env vars
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DATABASE_URL", "sqlite://database.db")

    # Change to tmp_path to avoid loading project .env
    monkeypatch.chdir(tmp_path)

    settings = Settings()

    assert settings.app_env == Environment.production
    assert settings.log_level == "DEBUG"
    assert settings.database_url == "sqlite://database.db"


def test_settings_dotenv_file(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch):
    """Settings read values from a local .env file when present."""
    # Clear live env
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    # Create a temporary .env
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "APP_ENV=production",
                "LOG_LEVEL=WARNING",
                "DATABASE_URL=sqlite://test_db.db",
            ]
        )
    )

    # Change CWD so Settings reads the tmp .env
    monkeypatch.chdir(tmp_path)

    settings = Settings()

    assert settings.app_env == Environment.production
    assert settings.log_level == "WARNING"
    assert settings.database_url == "sqlite://test_db.db"

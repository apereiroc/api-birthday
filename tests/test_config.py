from app.config import Settings, Environment
from pytest import MonkeyPatch
import pathlib


def test_settings_defaults_tmp_env(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch):
    """Defaults load when no env vars are set."""

    # Ensure env vars are unset
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    # Change to tmp_path to avoid loading project .env
    monkeypatch.chdir(tmp_path)

    settings = Settings()

    assert settings.app_env == Environment.development
    assert settings.log_level == "INFO"


def test_settings_env_overrides(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch):
    """Environment variables override defaults."""

    # Set env vars
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    # Change to tmp_path to avoid loading project .env
    monkeypatch.chdir(tmp_path)

    settings = Settings()

    assert settings.app_env == Environment.production
    assert settings.log_level == "DEBUG"


def test_settings_dotenv_file(tmp_path: pathlib.Path, monkeypatch: MonkeyPatch):
    """Settings read values from a local .env file when present."""
    # Clear live env
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    # Create a temporary .env
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "APP_ENV=production",
                "LOG_LEVEL=WARNING",
            ]
        )
    )

    # Change CWD so Settings reads the tmp .env
    monkeypatch.chdir(tmp_path)

    settings = Settings()

    assert settings.app_env == Environment.production
    assert settings.log_level == "WARNING"

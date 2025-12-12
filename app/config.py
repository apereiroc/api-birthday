from enum import Enum
from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    development = "development"
    production = "production"


class Settings(BaseSettings):
    """
    Typed settings loaded from environment variables with `.env` support.

    Overrides follow Pydantic Settings rules. In tests, you can pass `_env_file`.
    """

    app_env: Environment = Field(default=Environment.development)
    log_level: str = Field(
        default="info",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL",
    )

    @field_validator("app_env", mode="before")
    @classmethod
    def normalize_app_env(cls, v: str | Environment) -> str:
        """Normalise app_env to lowercase string for enum matching."""
        if isinstance(v, Environment):
            return v.value
        return v.lower()

    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, v: str) -> str:
        """Normalise log level to uppercase."""
        v_upper = v.upper()
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v_upper not in allowed:
            raise ValidationError(f"log_level must be one of {allowed}, got '{v}'")
        return v_upper

    # configure `.env` loading and allow missing extra variables
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        extra="ignore",
    )


settings = Settings()

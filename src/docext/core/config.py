"""Application settings. The only place that reads environment variables."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration, loaded from env vars prefixed `DOCEXT_` and an optional `.env`."""

    model_config = SettingsConfigDict(env_prefix="DOCEXT_", env_file=".env", extra="ignore")

    env: str = "dev"
    log_level: str = "INFO"
    default_model: str = "mock:echo"
    max_upload_mb: int = 20
    max_input_chars: int = 200_000
    provider_timeout_s: float = 60.0
    provider_max_retries: int = 2
    mock_fixture_dir: Path | None = None

    # Vendor credentials keep their vendor-standard env var names (no DOCEXT_ prefix).
    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_base_url: str = Field(
        default="https://api.openai.com/v1", validation_alias="OPENAI_BASE_URL"
    )
    anthropic_api_key: str | None = Field(default=None, validation_alias="ANTHROPIC_API_KEY")
    anthropic_base_url: str = Field(
        default="https://api.anthropic.com", validation_alias="ANTHROPIC_BASE_URL"
    )
    ollama_base_url: str = Field(
        default="http://localhost:11434", validation_alias="OLLAMA_BASE_URL"
    )

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()

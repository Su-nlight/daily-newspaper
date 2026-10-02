"""Centralized settings. Every value that could differ between environments
(the Groq model name included) is read from here — nothing else in the
codebase should hardcode a model name or read `os.environ` directly.
"""

from functools import lru_cache
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Never logged, never returned in any API response — see app/services/llm.py.
    groq_api_key: str | None = None

    # The one place the default model name lives. Override with GROQ_MODEL.
    groq_model: str = "llama-3.3-70b-versatile"

    groq_timeout_seconds: float = 20.0
    groq_max_tokens: int = 800
    groq_temperature: float = 0.3

    # Comma-separated in the environment, e.g.
    # CORS_ALLOW_ORIGINS=http://localhost:3000,https://dailysignal.example.com
    cors_allow_origins: Annotated[list[str], NoDecode] = ["http://localhost:3000"]

    environment: str = "development"

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def _split_csv(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def groq_configured(self) -> bool:
        return bool(self.groq_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()

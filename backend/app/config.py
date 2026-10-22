"""Centralized settings. Every value that could differ between environments
(the Groq model name included) is read from here — nothing else in the
codebase should hardcode a model name or read `os.environ` directly.
"""

from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Never logged, never returned in any API response — see app/services/llm.py.
    groq_api_key: str | None = None

    # The one place the default model name lives. Override with GROQ_MODEL.
    # llama-3.3-70b-versatile is Enterprise-only on Groq (contact-sales
    # access) — a standard developer key gets a 404 for it.
    # openai/gpt-oss-20b is a current standard Production-tier model.
    groq_model: str = "openai/gpt-oss-20b"

    groq_timeout_seconds: float = 20.0
    groq_max_tokens: int = 800
    groq_temperature: float = 0.3

    # Comma-separated in the environment, e.g.
    # CORS_ALLOW_ORIGINS=http://localhost:3000,https://dailysignal.example.com
    cors_allow_origins: Annotated[list[str], NoDecode] = ["http://localhost:3000"]

    environment: str = "development"

    # ---- Module 09: content pipeline -------------------------------------
    # SQLite file holding fetched articles, story clusters and editions. A
    # relative path is resolved against backend/ (not the process cwd) so the
    # server and the scheduled CLI always agree on the file.
    database_path: str = "app/data/daily_signal.db"

    # Which content the read endpoints serve:
    #   auto     - generated pipeline content when any exists, else the seed
    #              corpus (lookups by explicit id may still fall back to seed)
    #   pipeline - generated content only; never the seed corpus
    #   seed     - the committed mock corpus only (pre-Module-09 behaviour)
    content_source: Literal["auto", "pipeline", "seed"] = "auto"

    # JSON file listing the sources to ingest. Defaults to the bundled list.
    pipeline_sources_file: str | None = None

    # LLM summarization of story clusters. Skipped automatically when
    # GROQ_API_KEY is unset; stories then get deterministic extractive text.
    pipeline_use_llm: bool = True
    pipeline_max_llm_stories: int = 20

    pipeline_lookback_hours: int = 72
    pipeline_fetch_timeout_seconds: float = 15.0
    pipeline_fetch_concurrency: int = 6
    pipeline_max_response_bytes: int = 5_000_000
    pipeline_user_agent: str = "DailySignalBot/0.1 (+https://github.com/Su-nlight/daily-newspaper)"
    pipeline_retention_days: int = 90

    # Edition shaping.
    edition_timezone: str = "UTC"
    edition_max_stories: int = 30
    # Regions the shared (non-personalized) front page favours.
    edition_regions: Annotated[list[str], NoDecode] = ["global"]

    # Optional credentials for sources that need them. Sources reference these
    # by setting name (see app/data/pipeline_sources.json) - never inline.
    newsapi_key: str | None = None
    nvd_api_key: str | None = None
    github_token: str | None = None

    @field_validator("cors_allow_origins", "edition_regions", mode="before")
    @classmethod
    def _split_csv(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def resolved_database_path(self) -> Path:
        path = Path(self.database_path)
        if path.is_absolute():
            return path
        return Path(__file__).resolve().parent.parent / path

    @property
    def groq_configured(self) -> bool:
        return bool(self.groq_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()

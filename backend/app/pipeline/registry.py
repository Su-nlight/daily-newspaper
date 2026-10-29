"""Loads the configured sources. Credentials are resolved from Settings by
name, so the JSON file can be committed safely."""

import json
import logging
from pathlib import Path

from app.config import Settings
from app.pipeline.schemas import SourceConfig

logger = logging.getLogger("daily_signal.pipeline")

DEFAULT_SOURCES_PATH = Path(__file__).resolve().parent.parent / "data" / "pipeline_sources.json"


class SourceConfigError(ValueError):
    pass


def load_sources(path: Path | str | None = None) -> list[SourceConfig]:
    source_path = Path(path) if path else DEFAULT_SOURCES_PATH
    try:
        raw = json.loads(source_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SourceConfigError(f"Cannot read sources file {source_path}: {exc}") from exc

    entries = raw.get("sources") if isinstance(raw, dict) else raw
    if not isinstance(entries, list):
        raise SourceConfigError('Sources file must be a list or {"sources": [...]}.')

    sources = [SourceConfig(**entry) for entry in entries]
    ids = [source.id for source in sources]
    duplicates = {i for i in ids if ids.count(i) > 1}
    if duplicates:
        raise SourceConfigError(f"Duplicate source ids: {sorted(duplicates)}")
    return sources


def source_secret(source: SourceConfig, settings: Settings) -> str | None:
    if not source.api_key_setting:
        return None
    value = getattr(settings, source.api_key_setting, None)
    return value if isinstance(value, str) and value else None


def active_sources(
    sources: list[SourceConfig], settings: Settings
) -> tuple[list[SourceConfig], list[str]]:
    """Enabled sources whose required credential (if any) is present, plus
    human-readable notes for the ones skipped for lack of one."""
    active: list[SourceConfig] = []
    skipped: list[str] = []
    for source in sources:
        if not source.enabled:
            continue
        needs_key = bool(source.api_key_setting) and source.api_key_required
        if needs_key and source_secret(source, settings) is None:
            skipped.append(f"{source.id}: {str(source.api_key_setting).upper()} is not set")
            continue
        active.append(source)
    return active, skipped

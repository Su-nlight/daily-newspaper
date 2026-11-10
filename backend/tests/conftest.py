"""Hermetic tests: never read a developer's real pipeline database, and never
let one test's settings leak into another."""

import pytest

from app.config import get_settings
from app.pipeline.store import get_store


@pytest.fixture(autouse=True)
def _isolated_content(tmp_path, monkeypatch):
    # Points at a database that does not exist, so the seed corpus is served
    # (exactly the behaviour tests written before Module 09 expect).
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "no-pipeline-yet.db"))
    monkeypatch.delenv("CONTENT_SOURCE", raising=False)
    get_settings.cache_clear()
    get_store.cache_clear()
    yield
    get_settings.cache_clear()
    get_store.cache_clear()

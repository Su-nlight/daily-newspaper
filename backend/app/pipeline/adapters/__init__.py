"""Importing this package registers every built-in adapter."""

from app.pipeline.adapters import arxiv, github, newsapi, nvd, rss  # noqa: F401
from app.pipeline.adapters.base import (
    FetchContext,
    FetchError,
    SourceAdapter,
    get_adapter,
    register_adapter,
    registered_kinds,
)

__all__ = [
    "FetchContext",
    "FetchError",
    "SourceAdapter",
    "get_adapter",
    "register_adapter",
    "registered_kinds",
]

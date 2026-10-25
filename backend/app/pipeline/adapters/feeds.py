"""RSS 2.0 / RSS 1.0 (RDF) / Atom parsing, namespace-agnostic.

Uses defusedxml: feeds are untrusted input, and stdlib ElementTree is open to
entity-expansion ("billion laughs") attacks.
"""

import re
from typing import Any
from xml.etree.ElementTree import Element

from defusedxml import ElementTree as SafeET
from defusedxml.common import DefusedXmlException

from app.pipeline.adapters.base import FetchError
from app.pipeline.schemas import RawItem, SourceConfig
from app.pipeline.textutil import collapse_ws, parse_datetime

_IMG_SRC_RE = re.compile(r"""<img[^>]+src=["']([^"']+)["']""", re.IGNORECASE)


def local_name(tag: object) -> str:
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def parse_xml(body: bytes) -> Element:
    try:
        return SafeET.fromstring(body)
    except DefusedXmlException as exc:
        raise FetchError("Feed uses disallowed XML constructs (entities/DTD).") from exc
    except SafeET.ParseError as exc:
        raise FetchError("Feed is not well-formed XML.") from exc


def children(element: Element, name: str) -> list[Element]:
    return [child for child in element if local_name(child.tag) == name]


def child_text(element: Element, *names: str) -> str:
    for name in names:
        for child in children(element, name):
            text = "".join(child.itertext()).strip()
            if text:
                return text
    return ""


def _entry_link(entry: Element) -> str:
    # Atom: <link rel="alternate" href="..."/>; RSS: <link>text</link>.
    fallback = ""
    for link in children(entry, "link"):
        href = (link.get("href") or "").strip()
        text = (link.text or "").strip()
        rel = link.get("rel", "alternate")
        if href and rel == "alternate":
            return href
        if href and not fallback:
            fallback = href
        if text:
            return text
    if fallback:
        return fallback
    guid = child_text(entry, "guid", "id")
    return guid if guid.startswith("http") else ""


def _entry_image(entry: Element, html_blob: str) -> str | None:
    for child in entry:
        name = local_name(child.tag)
        url = (child.get("url") or "").strip()
        if not url:
            continue
        kind = (child.get("type") or child.get("medium") or "").lower()
        if name == "thumbnail" or (name == "content" and kind.startswith("image")):
            return url
        if name == "content" and not kind and re.search(r"\.(jpe?g|png|webp|gif)(\?|$)", url, re.I):
            return url
        if name == "enclosure" and kind.startswith("image"):
            return url
    match = _IMG_SRC_RE.search(html_blob)
    return match.group(1) if match else None


def parse_feed(body: bytes, source: SourceConfig) -> list[RawItem]:
    root = parse_xml(body)
    root_name = local_name(root.tag)

    if root_name == "feed":  # Atom
        entries = children(root, "entry")
    elif root_name in {"rss", "RDF", "rdf"}:  # RSS 2.0 / RSS 1.0
        channel = next(iter(children(root, "channel")), None)
        entries = (children(channel, "item") if channel is not None else []) + children(
            root, "item"
        )
    else:
        raise FetchError(f"Unrecognised feed format <{root_name}>.")

    items: list[RawItem] = []
    for entry in entries:
        title = collapse_ws(child_text(entry, "title"))
        url = _entry_link(entry)
        if not title or not url:
            continue

        summary_html = child_text(entry, "description", "summary")
        content_html = child_text(entry, "encoded", "content")
        published = parse_datetime(
            child_text(entry, "pubDate", "published", "date", "updated", "issued")
        )
        tags = [
            (cat.text or cat.get("term") or "").strip()
            for cat in children(entry, "category")
            if (cat.text or cat.get("term"))
        ]
        extra: dict[str, Any] = {}
        author = child_text(entry, "author", "creator")
        if author:
            extra["author"] = collapse_ws(author)

        items.append(
            RawItem(
                source_id=source.id,
                source_name=source.name,
                kind=source.kind,
                title=title,
                url=url,
                summary=summary_html,
                content=content_html,
                published_at=published,
                image=_entry_image(entry, content_html or summary_html),
                tags=tags[:10],
                extra=extra,
            )
        )
    return items

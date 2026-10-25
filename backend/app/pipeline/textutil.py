"""Small, dependency-free helpers shared by adapters and normalization."""

import html
import ipaddress
import re
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

_WS_RE = re.compile(r"\s+")
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"“‘(])")

# Query parameters that identify a *visit*, not a document.
_TRACKING_PARAMS = {
    "fbclid", "gclid", "dclid", "msclkid", "mc_cid", "mc_eid", "igshid", "yclid",
    "ref", "ref_src", "ref_url", "cmpid", "campaign", "spm", "_hsenc", "_hsmi",
    "mkt_tok", "oly_enc_id", "oly_anon_id", "ncid", "ocid", "guccounter",
}  # fmt: skip
_BLOCK_TAGS = {"p", "div", "br", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "pre"}
_SKIP_TAGS = {"script", "style", "noscript", "template", "svg", "iframe"}


def collapse_ws(text: str) -> str:
    return _WS_RE.sub(" ", text).strip()


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _SKIP_TAGS:
            self._skip_depth += 1
        elif tag in _BLOCK_TAGS:
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1
        elif tag in _BLOCK_TAGS:
            self.parts.append(" ")

    def handle_data(self, data: str) -> None:
        if not self._skip_depth:
            self.parts.append(data)


def strip_html(value: str | None) -> str:
    """Visible text of an HTML (or plain text) fragment, entities decoded and
    whitespace collapsed. Never raises on malformed markup."""
    if not value:
        return ""
    if "<" not in value and "&" not in value:
        return collapse_ws(value)
    parser = _TextExtractor()
    try:
        parser.feed(value)
        parser.close()
    except Exception:  # pragma: no cover - HTMLParser is very forgiving
        return collapse_ws(html.unescape(re.sub(r"<[^>]+>", " ", value)))
    return collapse_ws(html.unescape("".join(parser.parts)))


_MD_LINK_RE = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
_MD_NOISE_RE = re.compile(r"(^|\s)(#{1,6}|[-*+]|>|\d+\.)\s+|[`*_~]{1,3}")


def strip_markdown(value: str | None) -> str:
    """Plain text from Markdown release notes: links keep their label, and
    heading/bullet/emphasis markers go. Not a parser - just enough to make a
    readable summary line out of a GitHub release body."""
    if not value:
        return ""
    text = _MD_LINK_RE.sub(r"\1", value)
    text = "\n".join(_MD_NOISE_RE.sub(r"\1", line) for line in text.splitlines())
    return strip_html(text)


def truncate(text: str, limit: int) -> str:
    """Cut at a word boundary and add an ellipsis; no-op if it already fits."""
    text = text.strip()
    if len(text) <= limit:
        return text
    cut = text[: limit - 1]
    if " " in cut[limit // 2 :]:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(" ,;:-–—") + "…"


def split_sentences(text: str) -> list[str]:
    text = collapse_ws(text)
    return [s for s in _SENTENCE_RE.split(text) if s] if text else []


def lead_sentences(text: str, *, max_sentences: int = 2, max_chars: int = 300) -> str:
    """The first sentences of `text`, within a character budget."""
    picked: list[str] = []
    for sentence in split_sentences(text):
        candidate = " ".join([*picked, sentence])
        if picked and len(candidate) > max_chars:
            break
        picked.append(sentence)
        if len(picked) >= max_sentences:
            break
    return truncate(" ".join(picked), max_chars)


def parse_datetime(value: str | None) -> datetime | None:
    """RFC 822 (RSS) or ISO 8601 (Atom/JSON) into an aware UTC datetime."""
    if not value:
        return None
    value = value.strip()
    parsed: datetime | None = None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        parsed = None
    if parsed is None:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def is_public_http_url(url: str | None) -> bool:
    """True for an absolute http(s) URL with a real, non-local host. Everything
    that ends up in an <a href> or an `image` field passes through this - it is
    what keeps `javascript:` / `file:` / internal-network URLs out of editions."""
    if not url or len(url) > 2048:
        return False
    try:
        parts = urlsplit(url.strip())
    except ValueError:
        return False
    if parts.scheme not in {"http", "https"} or not parts.hostname:
        return False
    host = parts.hostname.lower()
    if host == "localhost" or host.endswith((".local", ".internal", ".localhost")):
        return False
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return "." in host
    return address.is_global


def canonicalize_url(url: str | None) -> str | None:
    """A stable identity for a document URL: https, lower-case host without
    `www.`, no fragment, no tracking parameters, sorted query, no trailing
    slash. Returns None for anything that isn't a public http(s) URL."""
    if not is_public_http_url(url):
        return None
    assert url is not None
    parts = urlsplit(url.strip())
    host = (parts.hostname or "").lower().removeprefix("www.")
    port = parts.port
    netloc = host if port in (None, 80, 443) else f"{host}:{port}"
    path = re.sub(r"/{2,}", "/", parts.path or "/")
    if len(path) > 1:
        path = path.rstrip("/")
    query = sorted(
        (k, v)
        for k, v in parse_qsl(parts.query, keep_blank_values=False)
        if not k.lower().startswith("utm_") and k.lower() not in _TRACKING_PARAMS
    )
    return urlunsplit(("https", netloc, path, urlencode(query), ""))

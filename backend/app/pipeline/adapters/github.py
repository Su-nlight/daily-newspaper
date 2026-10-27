"""GitHub adapter: recent *releases* of watched repositories.

`source.params`: `repos` (["owner/name", ...]), `include_prereleases` (False).
Works without a token (60 req/h); set GITHUB_TOKEN for more headroom.
One unreachable repo doesn't fail the others.
"""

import json
import logging
from typing import Any

from app.pipeline.adapters.base import FetchContext, FetchError, http_get, register_adapter
from app.pipeline.schemas import RawItem, SourceConfig
from app.pipeline.textutil import collapse_ws, parse_datetime, strip_markdown, truncate

logger = logging.getLogger("daily_signal.pipeline")


class GithubAdapter:
    async def fetch(self, source: SourceConfig, ctx: FetchContext) -> list[RawItem]:
        repos: list[str] = list(source.params.get("repos", []))
        if not repos:
            raise FetchError("GitHub source has no `repos` configured.")

        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if ctx.secret:
            headers["Authorization"] = f"Bearer {ctx.secret}"

        items: list[RawItem] = []
        failures = 0
        for repo in repos:
            try:
                body = await http_get(
                    ctx,
                    f"{source.url.rstrip('/')}/repos/{repo}/releases",
                    params={"per_page": 5},
                    headers=headers,
                )
                items.extend(parse_releases(body, source, repo))
            except FetchError as exc:
                failures += 1
                logger.warning("GitHub repo %s skipped: %s", repo, exc)
        if failures == len(repos):
            raise FetchError(f"All {len(repos)} GitHub repositories failed.")
        return items


def _release_title(project: str, tag: str, name: str) -> str:
    """ "langgraph v0.9.0 released" for plain version names; a descriptive
    release name ("Durable execution") is kept, prefixed by project and tag."""

    def bare(value: str) -> str:
        return value.lower().lstrip("v")

    if not name or bare(name) == bare(tag):
        return f"{project} {tag} released"
    if project.lower() in name.lower():
        return name
    return f"{project} {tag}: {name}"


def parse_releases(body: bytes, source: SourceConfig, repo: str) -> list[RawItem]:
    try:
        releases: Any = json.loads(body)
    except json.JSONDecodeError as exc:
        raise FetchError(f"GitHub returned invalid JSON for {repo}.") from exc
    if not isinstance(releases, list):
        raise FetchError(f"Unexpected GitHub response for {repo}.")

    include_pre = bool(source.params.get("include_prereleases", False))
    items: list[RawItem] = []
    for release in releases:
        if not isinstance(release, dict) or release.get("draft"):
            continue
        if release.get("prerelease") and not include_pre:
            continue
        tag = str(release.get("tag_name") or "").strip()
        url = release.get("html_url")
        if not tag or not url:
            continue
        name = collapse_ws(str(release.get("name") or tag))
        project = repo.split("/", 1)[-1]
        title = _release_title(project, tag, name)
        items.append(
            RawItem(
                source_id=source.id,
                source_name=source.name,
                kind="github",
                title=title,
                url=url,
                summary=truncate(strip_markdown(str(release.get("body") or "")), 600),
                published_at=parse_datetime(
                    release.get("published_at") or release.get("created_at")
                ),
                tags=[repo],
                extra={"repo": repo, "tag": tag, "prerelease": bool(release.get("prerelease"))},
            )
        )
    return items


register_adapter("github", GithubAdapter())

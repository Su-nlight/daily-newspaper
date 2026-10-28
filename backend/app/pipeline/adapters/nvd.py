"""CVE adapter backed by NIST's NVD API 2.0.

NVD publishes hundreds of CVEs a day, so this only emits those at or above
`params.min_cvss` (default 7.0, i.e. High/Critical) that were published since
the window start - otherwise one source would drown the front page.
An API key (NVD_API_KEY) is optional but raises the rate limit.
"""

import json
from datetime import timedelta
from typing import Any

from app.pipeline.adapters.base import FetchContext, FetchError, http_get, register_adapter
from app.pipeline.schemas import RawItem, SourceConfig
from app.pipeline.textutil import collapse_ws, lead_sentences, parse_datetime, truncate

_METRIC_KEYS = ("cvssMetricV40", "cvssMetricV31", "cvssMetricV30", "cvssMetricV2")


class NvdAdapter:
    async def fetch(self, source: SourceConfig, ctx: FetchContext) -> list[RawItem]:
        # NVD wants both bounds, and caps the range at 120 days.
        start = max(ctx.since, ctx.now - timedelta(days=120))
        params = {
            "pubStartDate": start.strftime("%Y-%m-%dT%H:%M:%S.000"),
            "pubEndDate": ctx.now.strftime("%Y-%m-%dT%H:%M:%S.000"),
            "resultsPerPage": 200,
        }
        headers = {"apiKey": ctx.secret} if ctx.secret else None
        body = await http_get(ctx, source.url, params=params, headers=headers)
        return parse_nvd(body, source)


def _best_cvss(cve: dict[str, Any]) -> tuple[float | None, str | None]:
    metrics = cve.get("metrics") or {}
    for key in _METRIC_KEYS:
        for metric in metrics.get(key) or []:
            data = metric.get("cvssData") or {}
            score = data.get("baseScore")
            if isinstance(score, int | float):
                severity = data.get("baseSeverity") or metric.get("baseSeverity")
                return float(score), (str(severity).upper() if severity else None)
    return None, None


def parse_nvd(body: bytes, source: SourceConfig) -> list[RawItem]:
    try:
        payload: Any = json.loads(body)
    except json.JSONDecodeError as exc:
        raise FetchError("NVD returned invalid JSON.") from exc
    vulnerabilities = payload.get("vulnerabilities") if isinstance(payload, dict) else None
    if not isinstance(vulnerabilities, list):
        raise FetchError("Unexpected NVD response shape.")

    min_cvss = float(source.params.get("min_cvss", 7.0))
    items: list[RawItem] = []
    for entry in vulnerabilities:
        cve = entry.get("cve") if isinstance(entry, dict) else None
        if not isinstance(cve, dict) or not cve.get("id"):
            continue
        cve_id = str(cve["id"])

        score, severity = _best_cvss(cve)
        if score is None or score < min_cvss:
            continue

        description = next(
            (
                collapse_ws(d.get("value", ""))
                for d in cve.get("descriptions", [])
                if d.get("lang") == "en"
            ),
            "",
        )
        if not description:
            continue

        headline = truncate(lead_sentences(description, max_sentences=1, max_chars=110), 110)
        items.append(
            RawItem(
                source_id=source.id,
                source_name=source.name,
                kind="nvd",
                title=f"{cve_id}: {headline}",
                url=f"https://nvd.nist.gov/vuln/detail/{cve_id}",
                summary=description,
                published_at=parse_datetime(cve.get("published")),
                tags=["cve", "vulnerability"],
                extra={"cve_id": cve_id, "cvss": score, "severity": severity},
            )
        )
    return items


register_adapter("nvd", NvdAdapter())

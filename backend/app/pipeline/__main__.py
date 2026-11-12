"""Scheduler-facing CLI.

    python -m app.pipeline run [--date YYYY-MM-DD] [--no-llm] [--no-fetch] [--json]
    python -m app.pipeline sources
    python -m app.pipeline status

`run` is what a scheduler (cron, systemd timer, a GitHub Actions cron, a cloud
scheduler) should call once a day - it is safe to call more often. Exit codes:
0 ok / degraded / skipped, 1 failed (no edition could be produced), 2 bad usage.
"""

import argparse
import asyncio
import logging
import sys

from app.config import get_settings
from app.pipeline.registry import SourceConfigError, active_sources, load_sources
from app.pipeline.runner import run_pipeline
from app.pipeline.store import get_store


def _cmd_run(args: argparse.Namespace) -> int:
    report = asyncio.run(
        run_pipeline(
            use_llm=False if args.no_llm else None,
            edition_date=args.date,
            fetch=not args.no_fetch,
        )
    )
    if args.json:
        print(report.model_dump_json(indent=2))
    else:
        print(f"status: {report.status}   edition: {report.edition_id}   ({report.duration_ms} ms)")
        for source in report.sources:
            mark = "ok  " if source.ok else "FAIL"
            detail = f"{source.item_count} items" if source.ok else source.error
            print(f"  [{mark}] {source.source_id:<20} {detail}")
        for note in report.skipped_sources:
            print(f"  [skip] {note}")
        print(
            f"articles: {report.new_articles} new, {report.changed_articles} changed | "
            f"stories: {report.stories_created} created, {report.stories_updated} updated, "
            f"{report.stories_unchanged} unchanged ({report.multi_source_stories} multi-source)"
        )
        print(
            f"summaries: {report.summaries_llm} model, {report.summaries_reused} reused, "
            f"{report.summaries_extractive} extractive {report.summary_fallback_reasons or ''}"
        )
        for warning in report.warnings:
            print(f"  ! {warning}")
    return 1 if report.status == "failed" else 0


def _cmd_sources(_: argparse.Namespace) -> int:
    settings = get_settings()
    sources = load_sources(settings.pipeline_sources_file)
    active, skipped = active_sources(sources, settings)
    active_ids = {s.id for s in active}
    for source in sources:
        state = "active" if source.id in active_ids else "inactive"
        print(f"{state:<9}{source.id:<20}{source.kind:<10}{source.url}")
    for note in skipped:
        print(f"skipped: {note}")
    return 0


def _cmd_status(_: argparse.Namespace) -> int:
    settings = get_settings()
    store = get_store(str(settings.resolved_database_path))
    latest = store.latest_edition()
    print(f"database: {settings.resolved_database_path}")
    print(f"latest edition: {latest.id if latest else 'none'}")
    for run in store.recent_runs(3):
        print(f"  run {run['started_at']}: {run.get('status')} ({run.get('edition_id')})")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m app.pipeline")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="fetch, process and publish today's edition")
    run.add_argument("--date", help="edition date YYYY-MM-DD (default: today)")
    run.add_argument("--no-llm", action="store_true", help="extractive summaries only")
    run.add_argument("--no-fetch", action="store_true", help="rebuild from stored articles")
    run.add_argument("--json", action="store_true", help="print the full report as JSON")
    run.set_defaults(func=_cmd_run)
    sub.add_parser("sources", help="list configured sources").set_defaults(func=_cmd_sources)
    sub.add_parser("status", help="show the latest edition and runs").set_defaults(func=_cmd_status)

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    try:
        return int(args.func(args))
    except SourceConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

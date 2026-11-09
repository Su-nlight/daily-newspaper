"""Stage: story assembly. Turns clusters into `StoryDraft`s.

A story's id must survive re-runs even as its cluster grows (a third outlet
reports the same event tomorrow). So ids are *assigned once and remembered*:
a cluster that contains an already-known article inherits that article's story
id; only a cluster of entirely new articles mints a new one. This is the
mechanism that makes the pipeline idempotent - running it twice finds the same
clusters, maps them to the same ids, and updates rather than duplicates.
"""

import hashlib

from app.models.article import Article, SourceAttribution
from app.pipeline.classify import aggregate
from app.pipeline.dedupe import StoryCluster
from app.pipeline.metadata import extract_entities
from app.pipeline.schemas import CandidateArticle, StoryDraft
from app.pipeline.textutil import lead_sentences

MAX_SOURCES_PER_STORY = 8


def mint_story_id(members: list[CandidateArticle]) -> str:
    digest = hashlib.sha1("|".join(sorted(m.id for m in members)).encode()).hexdigest()
    return f"story-{digest[:12]}"


def evidence_hash(members: list[CandidateArticle]) -> str:
    """Changes iff what a summary would be written from changes."""
    parts = sorted(f"{m.id}\x1f{m.title}\x1f{m.summary}\x1f{m.content[:1500]}" for m in members)
    return hashlib.sha256("\x1e".join(parts).encode()).hexdigest()[:24]


def assign_story_ids(
    clusters: list[StoryCluster],
    membership: dict[str, str],
    story_created_at: dict[str, str],
) -> list[str]:
    """One id per cluster, in order. `membership` maps known article id ->
    story id; `story_created_at` breaks ties when a cluster spans several
    known stories (the oldest story keeps its id; the others are retired)."""
    claimed: set[str] = set()
    ids: list[str] = []
    for cluster in clusters:
        known = {membership[m.id] for m in cluster.members if m.id in membership}
        # Oldest known story wins; ISO timestamps sort lexically.
        candidates = sorted(
            (sid for sid in known if sid not in claimed),
            key=lambda sid: (story_created_at.get(sid, "~"), sid),
        )
        story_id = candidates[0] if candidates else mint_story_id(cluster.members)
        if story_id in claimed:  # a split cluster whose id is already taken
            story_id = mint_story_id(cluster.members)
        claimed.add(story_id)
        ids.append(story_id)
    return ids


def _attributions(
    members: list[CandidateArticle], primary: CandidateArticle
) -> list[SourceAttribution]:
    ordered = [primary, *(m for m in members if m.id != primary.id)]
    seen: set[tuple[str, str]] = set()
    sources: list[SourceAttribution] = []
    for member in ordered:
        key = (member.source.lower(), member.canonical_url)
        if key in seen:
            continue
        seen.add(key)
        sources.append(
            SourceAttribution(
                publisher=member.source,
                url=member.url,
                title=member.title,
                published_at=member.published_at,
                source_id=member.source_id,
            )
        )
    return sources[:MAX_SOURCES_PER_STORY]


def choose_primary(members: list[CandidateArticle]) -> CandidateArticle:
    """The member whose headline and link lead the story: the best-quality one
    that has text. NVD records are authoritative sources but their "title" is
    a truncated description, so a human-written headline wins when one exists
    (NVD stays in `sources` and still supplies the CVSS fact)."""
    for allow_synthetic in (False, True):
        for member in members:
            if member.summary and (allow_synthetic or member.kind != "nvd"):
                return member
    return members[0]


def build_draft(story_id: str, cluster: StoryCluster) -> StoryDraft:
    members = cluster.members  # best source first
    primary = choose_primary(members)
    classification = aggregate(members)
    summary = (
        lead_sentences(primary.summary, max_sentences=2, max_chars=300) if primary.summary else ""
    )

    article = Article(
        id=story_id,
        title=primary.title,
        summary=summary,
        content=summary or None,
        category=classification.category,
        source=primary.source,
        source_url=primary.url,
        published_at=min(m.published_at for m in members),
        image_url=next((m.image for m in members if m.image), None),
        topics=classification.topics,
        entities=extract_entities(members),
        region=classification.region,
        sources=_attributions(members, primary),
    )
    return StoryDraft(
        article=article,
        members=members,
        evidence_hash=evidence_hash(members),
        merge_reasons=sorted(cluster.reasons),
    )


def build_drafts(
    clusters: list[StoryCluster],
    membership: dict[str, str],
    story_created_at: dict[str, str],
) -> list[StoryDraft]:
    ids = assign_story_ids(clusters, membership, story_created_at)
    return [build_draft(story_id, cluster) for story_id, cluster in zip(ids, clusters, strict=True)]

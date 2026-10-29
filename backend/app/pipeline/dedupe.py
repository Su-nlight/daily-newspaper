"""Stage: deduplicate + cluster into stories.

Three signals, strongest first (Module 09):

1. canonical URL     - identical documents
2. normalized title  - the same headline, however it was decorated
3. semantic similarity - the same *event* described in different words

Strong signals merge unconditionally (the CVE-id set counts as one). Semantic
merges are conservative, because a wrong merge hides a story while a missed
merge just shows two stories about one event:

* both items must be within `window_hours` of each other;
* items citing *different* CVE ids never merge, however similar the prose;
* a publisher never merges with itself on similarity alone;
* merging two clusters needs the *average* similarity across them to clear a
  bar, not just one close pair - that is what stops A~B~C chaining.

"Semantic" similarity here is TF-IDF cosine over title + lead summary: cheap,
deterministic and explainable (the repo's existing stance is no ML model in
the loop). `SimilarityModel` is the seam for swapping in real embeddings.
"""

import math
import re
import unicodedata
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Protocol

from app.pipeline.schemas import CandidateArticle

_TOKEN_RE = re.compile(r"[a-z0-9]+(?:[.\-][a-z0-9]+)*")
_CVE_RE = re.compile(r"\bcve-\d{4}-\d{4,7}\b", re.IGNORECASE)
_TITLE_PREFIX_RE = re.compile(
    r"^(breaking|exclusive|update|updated|watch|opinion|analysis|report)\s*[:\-–—]\s*", re.I
)
_TITLE_SUFFIX_RE = re.compile(r"\s+[-–—|·]\s+[^-–—|·]{2,40}$")

_STOPWORDS = frozenset(
    """a an and are as at be been but by for from has have he her his how i in into is it its
    of on or our out over she so than that the their them they this to up was we were what when
    which who will with you your after before about new says said say could would should may
    also more most just not no then there these those via per percent cent""".split()
)


def normalize_title(title: str) -> str:
    """Lower-cased, accent-free, punctuation-free headline with decoration
    (``Breaking:`` prefixes, `` - Publisher`` suffixes) removed."""
    text = unicodedata.normalize("NFKD", title)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = _TITLE_PREFIX_RE.sub("", text.strip())
    text = _TITLE_SUFFIX_RE.sub("", text)
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text.lower()).split())


def _stem(token: str) -> str:
    return (
        token[:-1] if len(token) > 3 and token.endswith("s") and not token.endswith("ss") else token
    )


def tokenize(text: str) -> list[str]:
    return [_stem(t) for t in _TOKEN_RE.findall(text.lower()) if t not in _STOPWORDS and len(t) > 1]


def cve_ids(article: CandidateArticle) -> frozenset[str]:
    found = {m.upper() for m in _CVE_RE.findall(f"{article.title} {article.summary}")}
    if article.extra.get("cve_id"):
        found.add(str(article.extra["cve_id"]).upper())
    return frozenset(found)


# ----------------------------------------------------------------- similarity
class SimilarityModel(Protocol):
    def similarity(self, i: int, j: int) -> float: ...
    def candidate_pairs(self) -> Iterable[tuple[int, int]]: ...


# Below this many distinct informative terms a document says too little to be
# matched on similarity ("Weekly roundup" + two words of summary).
MIN_DISTINCT_TOKENS = 5


class TfidfSimilarity:
    def __init__(self, articles: list[CandidateArticle]) -> None:
        docs = [self._doc_tokens(a) for a in articles]
        self._rich = [len(set(tokens)) >= MIN_DISTINCT_TOKENS for tokens in docs]
        df: Counter[str] = Counter()
        for tokens in docs:
            df.update(set(tokens))
        n = len(docs)
        self._idf = {t: math.log((n + 1) / (c + 1)) + 1.0 for t, c in df.items()}

        self._vectors: list[dict[str, float]] = []
        for tokens in docs:
            tf = Counter(tokens)
            vec = {t: (1 + math.log(c)) * self._idf[t] for t, c in tf.items()}
            norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
            self._vectors.append({t: v / norm for t, v in vec.items()})

        # Inverted index over reasonably selective terms -> candidate pairs.
        self._max_df = max(8, int(0.2 * n))
        self._postings: dict[str, list[int]] = defaultdict(list)
        for index, tokens in enumerate(docs):
            for token in set(tokens):
                if df[token] <= self._max_df:
                    self._postings[token].append(index)
        self._cache: dict[tuple[int, int], float] = {}

    @staticmethod
    def _doc_tokens(article: CandidateArticle) -> list[str]:
        # The headline counts double: it is the most event-specific text.
        title = tokenize(article.title)
        return title + title + tokenize(article.summary[:400])

    def similarity(self, i: int, j: int) -> float:
        key = (i, j) if i < j else (j, i)
        if key not in self._cache:
            a, b = self._vectors[key[0]], self._vectors[key[1]]
            if len(a) > len(b):
                a, b = b, a
            self._cache[key] = sum(w * b.get(t, 0.0) for t, w in a.items())
        return self._cache[key]

    def candidate_pairs(self) -> Iterable[tuple[int, int]]:
        shared: Counter[tuple[int, int]] = Counter()
        for indices in self._postings.values():
            for x in range(len(indices)):
                for y in range(x + 1, len(indices)):
                    shared[(indices[x], indices[y])] += 1
        return [
            (i, j)
            for (i, j), count in shared.items()
            if count >= 2 and self._rich[i] and self._rich[j]
        ]


# -------------------------------------------------------------------- cluster
@dataclass
class StoryCluster:
    members: list[CandidateArticle]
    # Why items were merged: "canonical_url" | "title" | "cve" | "semantic".
    reasons: set[str] = field(default_factory=set)

    @property
    def publishers(self) -> set[str]:
        return {m.source.strip().lower() for m in self.members}


@dataclass(frozen=True)
class DedupeConfig:
    window_hours: float = 48.0
    similarity_threshold: float = 0.40  # the closest pair must reach this...
    average_threshold: float = 0.28  # ...and the clusters on average this
    min_title_tokens: int = 4  # shorter normalized titles are too generic to equate


def cluster_articles(
    articles: list[CandidateArticle],
    *,
    config: DedupeConfig | None = None,
    model_factory: Callable[[list[CandidateArticle]], SimilarityModel] = TfidfSimilarity,
) -> list[StoryCluster]:
    cfg = config or DedupeConfig()
    n = len(articles)
    if n == 0:
        return []

    cves = [cve_ids(a) for a in articles]
    window = timedelta(hours=cfg.window_hours)

    parent = list(range(n))
    groups: dict[int, list[int]] = {i: [i] for i in range(n)}
    reasons: dict[int, set[str]] = {i: set() for i in range(n)}

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int, reason: str) -> None:
        ra, rb = find(a), find(b)
        if ra == rb:
            reasons[ra].add(reason)
            return
        if len(groups[ra]) < len(groups[rb]):
            ra, rb = rb, ra
        parent[rb] = ra
        groups[ra].extend(groups.pop(rb))
        reasons[ra] |= reasons.pop(rb) | {reason}

    def cve_conflict(i: int, j: int) -> bool:
        return bool(cves[i] and cves[j] and cves[i].isdisjoint(cves[j]))

    # --- 1-2. strong signals -------------------------------------------------
    by_url: dict[str, list[int]] = defaultdict(list)
    by_title: dict[str, list[int]] = defaultdict(list)
    by_cves: dict[frozenset[str], list[int]] = defaultdict(list)
    for i, a in enumerate(articles):
        by_url[a.canonical_url].append(i)
        norm = normalize_title(a.title)
        if len(norm.split()) >= cfg.min_title_tokens:
            by_title[norm].append(i)
        if cves[i]:
            by_cves[cves[i]].append(i)

    for index_map, reason in ((by_url, "canonical_url"), (by_title, "title"), (by_cves, "cve")):
        for indices in index_map.values():
            for other in indices[1:]:
                if reason == "title" and abs(
                    articles[indices[0]].published_at - articles[other].published_at
                ) > timedelta(days=7):
                    continue  # a recycled headline, not the same event
                union(indices[0], other, reason)

    # --- 3. semantic similarity ----------------------------------------------
    model = model_factory(articles)
    edges = []
    for i, j in model.candidate_pairs():
        if cve_conflict(i, j):
            continue
        if abs(articles[i].published_at - articles[j].published_at) > window:
            continue
        score = model.similarity(i, j)
        if score >= cfg.similarity_threshold:
            edges.append((score, i, j))
    edges.sort(key=lambda e: (-e[0], e[1], e[2]))

    for _, i, j in edges:
        ri, rj = find(i), find(j)
        if ri == rj:
            continue
        gi, gj = groups[ri], groups[rj]
        pubs_i = {articles[k].source.strip().lower() for k in gi}
        pubs_j = {articles[k].source.strip().lower() for k in gj}
        if pubs_i & pubs_j:
            continue  # one publisher is not corroboration of itself
        if any(cve_conflict(a, b) for a in gi for b in gj):
            continue
        pair_scores = [model.similarity(a, b) for a in gi for b in gj]
        if sum(pair_scores) / len(pair_scores) < cfg.average_threshold:
            continue
        union(i, j, "semantic")

    clusters = [
        StoryCluster(
            members=sorted(
                (articles[k] for k in members),
                key=lambda m: (-m.source_quality, m.published_at, m.id),
            ),
            reasons=reasons[root],
        )
        for root, members in groups.items()
    ]
    clusters.sort(
        key=lambda c: (-max(m.published_at for m in c.members).timestamp(), c.members[0].id)
    )
    return clusters

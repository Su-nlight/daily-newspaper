"""Stage: metadata extraction - named entities for a story.

Deterministic: identifiers (CVE ids), a gazetteer of well-known organisations
and products, acronyms, and proper-noun phrases from sentence-case text.
Headlines are Title Case, so proper-noun phrases are only mined from the body
(where capitalisation actually means something).
"""

import re
from collections import Counter

from app.pipeline import taxonomy as tx
from app.pipeline.schemas import CandidateArticle

MAX_ENTITIES = 8

_CVE_RE = re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.IGNORECASE)
_ACRONYM_RE = re.compile(r"\b[A-Z]{2,6}\b")
_PHRASE_RE = re.compile(r"\b[A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+){0,3}\b")
_GAZETTEER_RE = re.compile(
    r"(?<![A-Za-z0-9])("
    + "|".join(sorted(map(re.escape, tx.KNOWN_ENTITIES), key=len, reverse=True))
    + r")(?![A-Za-z0-9])"
)

_NOT_ENTITIES = frozenset(
    """The A An This That These Those It Its He She They We You I In On At For From With By As Of
    To And But Or If When While After Before During Over Under Monday Tuesday Wednesday Thursday
    Friday Saturday Sunday January February March April May June July August September October
    November December Today Yesterday Tomorrow However Meanwhile According Some Many Most Several
    One Two Three New Our Their His Her Is Are Was Were Will Would Could Should Can Might Also
    Series Updated Added Fixed Changed Release Version Breaking Note Notes""".split()
)
# Acronyms too generic to be a useful entity.
_GENERIC_ACRONYMS = frozenset(
    "AI IT US UK EU CEO CTO CFO API USD FAQ PM AM PDF URL HTML HTTP".split()
)


def extract_entities(articles: list[CandidateArticle]) -> list[str]:
    counts: Counter[str] = Counter()
    first_seen: dict[str, int] = {}

    def add(entity: str, weight: int = 1) -> None:
        counts[entity] += weight
        first_seen.setdefault(entity, len(first_seen))

    for article in articles:
        title = article.title
        body = f"{article.summary} {article.content[:1500]}"
        text = f"{title}. {body}"

        for cve in _CVE_RE.findall(text):
            add(cve.upper(), 3)
        if article.extra.get("cve_id"):
            add(str(article.extra["cve_id"]).upper(), 3)

        for match in _GAZETTEER_RE.findall(text):
            add(match, 2)
        for acronym in _ACRONYM_RE.findall(text):
            if acronym not in _GENERIC_ACRONYMS and acronym not in tx.KNOWN_ENTITIES:
                add(acronym)

        if article.kind == "github":
            continue  # release notes are Markdown fragments, not prose
        for sentence in re.split(r"(?<=[.!?])\s+", body):
            words = sentence.split()
            for match in _PHRASE_RE.finditer(sentence):
                phrase = match.group(0)
                # Skip a lone capitalised word that just starts the sentence.
                starts_sentence = bool(words) and sentence.lstrip().startswith(phrase.split()[0])
                if phrase in _NOT_ENTITIES or phrase in _GENERIC_ACRONYMS:
                    continue
                if starts_sentence and " " not in phrase:
                    continue
                if phrase.split()[0] in _NOT_ENTITIES:
                    phrase = " ".join(phrase.split()[1:])
                    if not phrase:
                        continue
                add(phrase)

    # Drop a name that is merely part of a longer one ("Hugging" vs "Hugging Face").
    names = list(counts)
    kept = [
        n
        for n in names
        if not any(
            n != other and n.lower() in other.lower() and counts[other] >= counts[n]
            for other in names
        )
    ]
    ranked = sorted(kept, key=lambda n: (-counts[n], first_seen[n]))
    return ranked[:MAX_ENTITIES]

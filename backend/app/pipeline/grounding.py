"""Grounding verifier: the structural guarantee behind "the LLM must not
invent facts, statistics, quotes, sources or URLs" (Module 09).

A prompt can ask a model to behave; this module *checks* that it did. Any
generated text is compared against the evidence the model was given, and
rejected when it contains:

* a number, percentage or amount that appears nowhere in the evidence;
* a quotation that is not verbatim in the evidence;
* any URL (URLs only ever come from source metadata, never from text);
* a proper noun (company, product, person, place) absent from the evidence.

Rejection is cheap and safe: the pipeline falls back to deterministic
extractive text. The checks are deliberately conservative - a false rejection
costs a less fluent summary, a false acceptance costs a fabricated fact.
"""

import re
from dataclasses import dataclass

_CITATION_RE = re.compile(r"\[\d+\]")
_NUMBER_RE = re.compile(r"\d[\d,]*(?:\.\d+)?")
_QUOTE_RE = re.compile(r"[“\"]([^”\"]{1,400})[”\"]")
_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
_DOMAIN_RE = re.compile(
    r"\b[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:com|org|net|io|ai|dev|gov|edu|co|in|uk|app)\b",
    re.IGNORECASE,
)
_CAP_TOKEN_RE = re.compile(r"[A-Z][A-Za-z0-9]*(?:[-.][A-Za-z0-9]+)*")
_WORD_RE = re.compile(r"[a-z0-9]+(?:[-.][a-z0-9]+)*")

# Ordinary words that are capitalised only because they open a sentence, plus
# calendar words (the *numbers* in a date are verified separately). Any other
# capitalised word - including a sentence-initial one - must appear in the
# evidence. That is deliberately strict: an unusual opener ("Jensen ...") is
# indistinguishable from an invented name, and a false rejection merely falls
# back to extractive text.
_ALLOWED_CAPS = frozenset(
    """
    the a an this that these those it its they their he she we in on at for from with by as of to
    and but or if when while after before during under over according however also some many most
    several one two three four five new now today there here what which who why how all both each
    other another such more less after since until because although though meanwhile still yet
    officials researchers company companies users developers attackers analysts experts customers
    engineers teams organizations enterprises vendors maintainers regulators lawmakers investors
    additionally separately reportedly notably overall currently earlier later reuters meanwhile
    both either neither each every any no none customers startups startup security software
    hardware systems models model tools tool data cloud
    january february march april may june july august september october november december
    monday tuesday wednesday thursday friday saturday sunday q1 q2 q3 q4
    """.split()
)


def _norm(text: str) -> str:
    text = text.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    return " ".join(text.lower().split())


def _canonical_number(raw: str) -> str:
    cleaned = raw.replace(",", "").rstrip(".")
    try:
        value = float(cleaned)
    except ValueError:
        return cleaned
    return str(int(value)) if value == int(value) else repr(value)


def _variants(token: str) -> set[str]:
    base = token.lower().replace("’", "'")
    forms = {base, base.removesuffix("'s"), base.removesuffix("s"), base.removesuffix("'")}
    forms |= {part for form in list(forms) for part in re.split(r"[-.]", form) if len(part) > 1}
    return forms


class Evidence:
    """Everything the model was allowed to see, pre-digested for checking."""

    def __init__(self, texts: list[str]) -> None:
        self.text = "\n".join(texts)
        self.norm = _norm(self.text)
        # The `[n]` labels we put on evidence blocks are not facts: without this,
        # "5 companies" would be "supported" just because there are five blocks.
        self.numbers = {
            _canonical_number(n) for n in _NUMBER_RE.findall(_CITATION_RE.sub("", self.text))
        }
        self.words: set[str] = set()
        for word in _WORD_RE.findall(self.norm):
            self.words |= _variants(word)

    def has_word(self, token: str) -> bool:
        return bool(_variants(token) & self.words)


@dataclass
class GroundingResult:
    problems: list[str]

    @property
    def ok(self) -> bool:
        return not self.problems


def check_text(text: str, evidence: Evidence) -> GroundingResult:
    """Problems with `text` relative to `evidence`; empty list means grounded."""
    problems: list[str] = []
    body = _CITATION_RE.sub("", text)

    if _URL_RE.search(body):
        problems.append("contains a URL")
    for domain in _DOMAIN_RE.findall(body):
        if domain.lower() not in evidence.norm:
            problems.append(f"mentions unsupported domain '{domain}'")

    for raw in _NUMBER_RE.findall(body):
        if _canonical_number(raw) not in evidence.numbers:
            problems.append(f"unsupported number '{raw}'")

    for match in _QUOTE_RE.finditer(body):
        if _norm(match.group(1)) not in evidence.norm:
            problems.append(f"unsupported quotation '{match.group(1)[:40]}'")

    for match in _CAP_TOKEN_RE.finditer(body):
        token = match.group(0)
        lower = token.lower()
        if len(token) < 2 or lower in _CALENDAR or evidence.has_word(token):
            continue
        if lower in _ALLOWED_CAPS:
            continue
        problems.append(f"unsupported name '{token}'")

    # De-duplicate while keeping order.
    return GroundingResult(list(dict.fromkeys(problems)))


_CALENDAR = frozenset(
    "january february march april may june july august september october november december "
    "monday tuesday wednesday thursday friday saturday sunday".split()
)

"""Despite the name (matching the module's requested file structure), this
is deterministic prompt-context formatting, not LLM-based summarization —
adding a second model call here to summarize before answering would be
exactly the kind of unnecessary extra agent the module spec says to avoid.
Compacts retrieved articles into a numbered, citable block within a
character budget. A real abstractive step could replace this later without
changing generate_answer's interface.
"""

from app.models.article import Article

MAX_CONTEXT_CHARS = 6000


def format_context(documents: list[Article]) -> str:
    if not documents:
        return ""

    blocks: list[str] = []
    used = 0

    for index, doc in enumerate(documents, start=1):
        block = (
            f"[{index}] {doc.title}\n"
            f"Source: {doc.source} ({doc.published_at.date().isoformat()})\n"
            f"{doc.summary}\n"
        )
        if doc.what_happened:
            block += f"What happened: {doc.what_happened}\n"
        if doc.why_it_matters:
            block += f"Why it matters: {doc.why_it_matters}\n"
        if doc.key_facts:
            block += "Key facts: " + " ".join(doc.key_facts) + "\n"
        if used + len(block) > MAX_CONTEXT_CHARS:
            break
        blocks.append(block)
        used += len(block)

    return "\n".join(blocks)

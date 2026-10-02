import re

from app.graph.state import GraphState
from app.models.chat import ChatSourceRef

_CITATION_RE = re.compile(r"\[(\d+)\]")


def validate_format(state: GraphState) -> GraphState:
    """Builds the final `sources` list. Critically, every url here comes
    from a retrieved Article's own source_url — never from the raw model
    output — so the model cannot inject a fabricated URL into the
    response no matter what it generates. This is enforced structurally,
    not just by prompt instruction.
    """
    documents = state.get("retrieved_documents", [])
    answer = state.get("answer", "")

    if state.get("error") or not documents:
        return {"sources": []}

    cited_indexes = {int(match) for match in _CITATION_RE.findall(answer)}
    cited_sources = [
        ChatSourceRef(publisher=doc.source, url=doc.source_url, title=doc.title)
        for index, doc in enumerate(documents, start=1)
        if index in cited_indexes
    ]

    # The model was given context but didn't cite it inline — still surface
    # what was retrieved rather than leaving an unverifiable factual claim
    # with no attached sources.
    sources = cited_sources or [
        ChatSourceRef(publisher=doc.source, url=doc.source_url, title=doc.title)
        for doc in documents
    ]

    return {"sources": sources}

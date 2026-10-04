from app.graph.nodes.validate_format import validate_format
from app.services import sources


def test_validate_format_only_includes_cited_sources():
    docs = sources.list_articles()[:3]
    state = {"retrieved_documents": docs, "answer": "Some fact [1]. More context [3]."}

    result = validate_format(state)

    urls = {source.url for source in result["sources"]}
    assert urls == {docs[0].source_url, docs[2].source_url}


def test_validate_format_falls_back_to_all_documents_when_uncited():
    docs = sources.list_articles()[:2]
    state = {"retrieved_documents": docs, "answer": "A general summary with no citation markers."}

    result = validate_format(state)

    urls = {source.url for source in result["sources"]}
    assert urls == {docs[0].source_url, docs[1].source_url}


def test_validate_format_returns_no_sources_without_documents():
    result = validate_format({"retrieved_documents": [], "answer": "Hi there!"})
    assert result["sources"] == []


def test_validate_format_returns_no_sources_on_error():
    docs = sources.list_articles()[:1]
    state = {"retrieved_documents": docs, "answer": "oops [1]", "error": "llm_not_configured"}
    result = validate_format(state)
    assert result["sources"] == []


def test_validate_format_never_trusts_a_url_from_the_answer_text():
    """The whole point: even if the model's raw text contains something
    that looks like a URL, it must never end up in `sources` — only URLs
    that trace back to a retrieved Article can."""
    docs = sources.list_articles()[:1]
    state = {
        "retrieved_documents": docs,
        "answer": "According to https://not-a-real-source.example.com this is true [1].",
    }

    result = validate_format(state)

    assert len(result["sources"]) == 1
    assert result["sources"][0].url == docs[0].source_url
    assert "not-a-real-source" not in result["sources"][0].url

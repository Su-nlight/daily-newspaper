from unittest.mock import patch

from fastapi.testclient import TestClient

from app.graph.nodes.classify_query import classify_query
from app.graph.nodes.generate_answer import MAX_HISTORY_TURNS, build_messages
from app.graph.nodes.validate_format import validate_format
from app.main import app
from app.services import retrieval, sources

client = TestClient(app)


def test_every_edition_story_exists_in_the_corpus():
    for edition in sources.list_editions():
        assert edition.stories, edition.id
    assert sources.get_edition_by_id("edition-2026-09-22") is not None


def test_frontend_only_stories_are_now_retrievable():
    # Present in the frontend mock data but absent from the old hand-written
    # backend corpus — story chat used to find nothing for these.
    docs = retrieval.retrieve_for_query(query="tell me more", story_id="story-rust-backend-scale")
    assert docs
    assert docs[0].id == "story-rust-backend-scale"


def test_edition_scope_returns_edition_stories_without_keyword_match():
    edition = sources.get_edition_by_id("edition-2026-09-22")
    docs = retrieval.retrieve_for_query(
        query="zzqq xxyy", edition_id="edition-2026-09-22"
    )
    assert docs
    assert {d.id for d in docs} <= {s.id for s in edition.stories}


def test_search_results_scope_limits_the_pool():
    ids = ["story-rag-benchmark", "story-ai-debugger"]
    docs = retrieval.retrieve_for_query(query="summarize these", search_result_ids=ids)
    assert docs
    assert {d.id for d in docs} <= set(ids)


def test_empty_search_results_scope_returns_nothing():
    assert retrieval.retrieve_for_query(query="summarize these", search_result_ids=[]) == []


def test_unknown_edition_falls_back_to_unscoped_ranking():
    docs = retrieval.retrieve_for_query(query="zzqqxxnonsense", edition_id="edition-1999-01-01")
    assert docs == []


def test_scope_phrases_route_to_news():
    assert classify_query({"query": "summarize these results"})["query_type"] == "news"
    assert classify_query({"query": "what's the most important thing here"})["query_type"] == "news"


def test_build_messages_includes_recent_history_in_order():
    history = [
        {"role": "user", "content": "first question"},
        {"role": "assistant", "content": "first answer"},
    ]
    messages = build_messages(
        query="follow up", query_type="general", documents=[], history=history
    )
    assert [m["role"] for m in messages] == ["system", "user", "assistant", "user"]
    assert messages[1]["content"] == "first question"
    assert messages[-1]["content"] == "follow up"


def test_build_messages_caps_history():
    history = [{"role": "user", "content": f"q{i}"} for i in range(MAX_HISTORY_TURNS + 5)]
    messages = build_messages(query="x", query_type="general", documents=[], history=history)
    assert len(messages) == 1 + MAX_HISTORY_TURNS + 1
    assert messages[1]["content"] == "q5"


def test_story_context_includes_long_form_detail_in_the_prompt():
    doc = sources.get_article("story-ai-policy-2026")
    messages = build_messages(query="why", query_type="story", documents=[doc], history=[])
    assert "Why it matters:" in messages[-1]["content"]


def test_validate_format_keeps_original_citation_numbers():
    docs = sources.list_articles()[:3]
    result = validate_format({"retrieved_documents": docs, "answer": "Only the third [3]."})
    assert [s.index for s in result["sources"]] == [3]


def test_chat_endpoint_accepts_history_and_search_context():
    captured = {}

    def fake_completion(messages):
        captured["messages"] = messages
        return "Sure [1]."

    with patch("app.services.llm.generate_completion", side_effect=fake_completion):
        response = client.post(
            "/api/chat",
            json={
                "message": "summarize these results",
                "context": {
                    "search_query": "rag",
                    "search_result_ids": ["story-rag-benchmark"],
                },
                "history": [
                    {"role": "user", "content": "hi"},
                    {"role": "assistant", "content": "hello"},
                ],
            },
        )

    assert response.status_code == 200
    assert response.json()["sources"][0]["index"] == 1
    roles = [m["role"] for m in captured["messages"]]
    assert roles == ["system", "user", "assistant", "user"]
    assert "RAG" in captured["messages"][-1]["content"]


def test_chat_endpoint_rejects_unknown_history_role():
    response = client.post(
        "/api/chat",
        json={"message": "hi", "history": [{"role": "system", "content": "x"}]},
    )
    assert response.status_code == 422


def test_stream_done_event_includes_conversation_id_and_indexed_sources():
    with (
        patch(
            "app.services.llm.stream_completion",
            return_value=iter(["India proposes audits ", "[1]."]),
        ),
        client.stream(
            "POST",
            "/api/chat/stream",
            json={
                "message": "what changed",
                "conversation_id": "conv-9",
                "context": {"story_id": "story-ai-policy-2026"},
            },
        ) as response,
    ):
        body = "".join(response.iter_text())

    assert '"conversation_id": "conv-9"' in body
    assert '"index": 1' in body

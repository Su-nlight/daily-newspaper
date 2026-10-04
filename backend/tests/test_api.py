from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services import llm

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_today_edition():
    response = client.get("/api/edition/today")
    assert response.status_code == 200
    assert response.json()["date"]


def test_edition_not_found():
    response = client.get("/api/edition/1999-01-01")
    assert response.status_code == 404


def test_story_by_id():
    response = client.get("/api/stories/story-ai-policy-2026")
    assert response.status_code == 200
    assert response.json()["id"] == "story-ai-policy-2026"


def test_story_not_found():
    response = client.get("/api/stories/does-not-exist")
    assert response.status_code == 404


def test_list_stories_filtered_by_category():
    response = client.get("/api/stories", params={"category": "cybersecurity"})
    assert response.status_code == 200
    assert all(story["category"] == "cybersecurity" for story in response.json())


def test_search_endpoint():
    response = client.get("/api/search", params={"q": "semiconductor"})
    assert response.status_code == 200
    assert any(story["id"] == "story-semiconductor-alliance" for story in response.json())


def test_chat_empty_message_rejected():
    response = client.post("/api/chat", json={"message": "   "})
    assert response.status_code == 422


def test_chat_without_api_key_degrades_gracefully():
    # Forces the "not configured" path directly rather than relying on
    # GROQ_API_KEY being absent from the environment — on a machine with a
    # real .env configured, depending on ambient env state would make this
    # test flaky (and worse, could make it silently call the real Groq API
    # during a test run instead of testing the degraded path at all).
    with patch(
        "app.services.llm.get_groq_client",
        side_effect=llm.LLMConfigurationError("GROQ_API_KEY is not set."),
    ):
        response = client.post("/api/chat", json={"message": "hello"})

    assert response.status_code == 200
    body = response.json()
    assert "isn't configured" in body["message"]
    assert body["sources"] == []
    assert body["conversation_id"]


def test_chat_with_mocked_llm_returns_cited_sources():
    with patch(
        "app.services.llm.generate_completion",
        return_value="India proposed a new AI audit rule [1].",
    ):
        response = client.post(
            "/api/chat",
            json={"message": "what's today's AI news"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "India proposed a new AI audit rule [1]."
    assert len(body["sources"]) == 1
    assert body["sources"][0]["publisher"]
    assert body["sources"][0]["url"].startswith("https://")


def test_chat_preserves_provided_conversation_id():
    response = client.post(
        "/api/chat", json={"message": "hello", "conversation_id": "conv-123"}
    )
    assert response.json()["conversation_id"] == "conv-123"


def test_chat_stream_returns_sse_events():
    with (
        patch("app.services.llm.stream_completion", return_value=iter(["Hello", " there!"])),
        client.stream("POST", "/api/chat/stream", json={"message": "hello"}) as response,
    ):
        assert response.status_code == 200
        body = "".join(response.iter_text())

    assert 'data: {"type": "token", "content": "Hello"}' in body
    assert '"type": "done"' in body

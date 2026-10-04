from unittest.mock import patch

from app.graph.nodes.generate_answer import generate_answer
from app.services import llm, sources


def test_general_query_calls_llm_directly():
    state = {"query": "hello", "query_type": "general", "retrieved_documents": []}
    with patch("app.services.llm.generate_completion", return_value="Hi there!") as mock:
        result = generate_answer(state)

    assert result["answer"] == "Hi there!"
    mock.assert_called_once()


def test_empty_retrieval_skips_llm_entirely():
    with patch("app.services.llm.generate_completion") as mock:
        result = generate_answer(
            {"query": "today's news", "query_type": "news", "retrieved_documents": []}
        )

    mock.assert_not_called()
    assert "couldn't find" in result["answer"].lower()


def test_grounded_query_passes_context_to_llm():
    docs = sources.list_articles()[:2]
    with patch("app.services.llm.generate_completion", return_value="Answer [1].") as mock:
        result = generate_answer(
            {"query": "what happened", "query_type": "news", "retrieved_documents": docs}
        )

    assert result["answer"] == "Answer [1]."
    user_message = mock.call_args[0][0][1]["content"]
    assert docs[0].title in user_message
    assert "CONTEXT" in user_message


def test_missing_api_key_degrades_gracefully():
    state = {"query": "hello", "query_type": "general", "retrieved_documents": []}
    with patch(
        "app.services.llm.generate_completion",
        side_effect=llm.LLMConfigurationError("no key"),
    ):
        result = generate_answer(state)

    assert result["error"] == "llm_not_configured"
    assert "isn't configured" in result["answer"]


def test_llm_request_error_degrades_gracefully():
    with patch(
        "app.services.llm.generate_completion",
        side_effect=llm.LLMRequestError("Groq rate limit exceeded. Please try again shortly."),
    ):
        result = generate_answer(
            {"query": "hello", "query_type": "general", "retrieved_documents": []}
        )

    assert result["error"] == "llm_request_failed"
    assert "rate limit" in result["answer"].lower()

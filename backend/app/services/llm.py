"""The single place the Groq client is instantiated and called. No node or
service should import `groq` directly or build its own client — call
`generate_completion` / `stream_completion` from here instead, so the model
name, timeout, and error handling stay in one place.
"""

from collections.abc import Generator
from functools import lru_cache

from groq import APIStatusError, APITimeoutError, Groq, RateLimitError

from app.config import get_settings


class LLMConfigurationError(Exception):
    """Raised when GROQ_API_KEY isn't set. Callers should catch this and
    degrade to a clear, honest message rather than a 500."""


class LLMRequestError(Exception):
    """Raised for any Groq API failure once a request was actually made:
    rate limits, timeouts, and non-2xx responses all normalize to this."""


@lru_cache
def get_groq_client() -> Groq:
    settings = get_settings()
    if not settings.groq_configured:
        raise LLMConfigurationError("GROQ_API_KEY is not set.")
    return Groq(api_key=settings.groq_api_key, timeout=settings.groq_timeout_seconds)


def generate_completion(messages: list[dict[str, str]]) -> str:
    """Single-shot (non-streaming) completion. Used by the standard
    /api/chat graph path."""
    settings = get_settings()
    client = get_groq_client()

    try:
        response = client.chat.completions.create(
            model=settings.groq_model,
            messages=messages,  # type: ignore[arg-type]
            temperature=settings.groq_temperature,
            max_tokens=settings.groq_max_tokens,
        )
    except RateLimitError as exc:
        raise LLMRequestError("Groq rate limit exceeded. Please try again shortly.") from exc
    except APITimeoutError as exc:
        raise LLMRequestError("The AI service timed out. Please try again.") from exc
    except APIStatusError as exc:
        raise LLMRequestError(f"The AI service returned an error ({exc.status_code}).") from exc

    return response.choices[0].message.content or ""


def stream_completion(messages: list[dict[str, str]]) -> Generator[str, None, None]:
    """Yields text chunks as they arrive from Groq. Used by the
    /api/chat/stream SSE endpoint. Errors (including a missing API key,
    raised lazily on first iteration since this is a generator) surface the
    same exception types as generate_completion."""
    settings = get_settings()
    client = get_groq_client()

    try:
        stream = client.chat.completions.create(
            model=settings.groq_model,
            messages=messages,  # type: ignore[arg-type]
            temperature=settings.groq_temperature,
            max_tokens=settings.groq_max_tokens,
            stream=True,
        )
        for chunk in stream:
            # The SDK's overload resolution for stream=True isn't narrowed
            # here (a known limitation with keyword-argument literals);
            # chunk is always a ChatCompletionChunk at runtime.
            delta = chunk.choices[0].delta.content  # type: ignore[union-attr]
            if delta:
                yield delta
    except RateLimitError as exc:
        raise LLMRequestError("Groq rate limit exceeded. Please try again shortly.") from exc
    except APITimeoutError as exc:
        raise LLMRequestError("The AI service timed out. Please try again.") from exc
    except APIStatusError as exc:
        raise LLMRequestError(f"The AI service returned an error ({exc.status_code}).") from exc

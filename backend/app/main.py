import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import chat, edition, search, stories
from app.config import get_settings
from app.services.llm import LLMConfigurationError, LLMRequestError

logger = logging.getLogger("daily_signal")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Daily Signal API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(chat.router)
    app.include_router(edition.router)
    app.include_router(stories.router)
    app.include_router(search.router)

    # The chat graph already catches LLM errors internally and degrades to
    # a clear in-band message (see generate_answer.py) — these handlers are
    # a safety net for any LLM call made outside the graph, and for any
    # genuinely unexpected exception, so the API never leaks a raw
    # traceback to the frontend.
    @app.exception_handler(LLMConfigurationError)
    async def handle_llm_configuration_error(
        request: Request, exc: LLMConfigurationError
    ) -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": "The AI service isn't configured."})

    @app.exception_handler(LLMRequestError)
    async def handle_llm_request_error(request: Request, exc: LLMRequestError) -> JSONResponse:
        return JSONResponse(status_code=502, content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s", request.url.path)
        return JSONResponse(status_code=500, content={"detail": "An unexpected error occurred."})

    @app.get("/api/health")
    async def health() -> dict:
        return {"status": "ok", "groq_configured": settings.groq_configured}

    return app


app = create_app()

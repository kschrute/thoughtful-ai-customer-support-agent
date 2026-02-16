from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles

from backend.container import AppContainer
from backend.dependencies import get_chat_service
from backend.models import ChatRequest, ChatResponse
from backend.services.chat_service import ChatService
from backend.services.exceptions import ValidationError
from backend.services.kb_service import KnowledgeBaseService
from backend.services.llm_client import AutoLLMClient, LLMConfigurationError, LLMRequestError, env_default_timeout_seconds
from backend.services.rate_limiter import AsyncSlidingWindowRateLimiter, RateLimitExceeded, RateLimitedLLMClient
from backend.settings import load_settings


load_dotenv()

FRONTEND_DIST_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"
FRONTEND_INDEX_HTML = FRONTEND_DIST_DIR / "index.html"


def create_app() -> FastAPI:
    settings = load_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        timeout_seconds = env_default_timeout_seconds()
        http_client = httpx.AsyncClient(timeout=timeout_seconds)

        kb_service = KnowledgeBaseService.from_json(settings.kb_path)
        llm_client = AutoLLMClient(
            http_client=http_client,
            provider=settings.llm_provider,
            openai_api_key=settings.openai_api_key,
            openai_model=settings.openai_model,
            gemini_api_key=settings.gemini_api_key,
            gemini_model=settings.gemini_model,
        )

        llm_rate_limiter = AsyncSlidingWindowRateLimiter(max_requests=10, window_seconds=3600)
        rate_limited_llm_client = RateLimitedLLMClient(llm=llm_client, limiter=llm_rate_limiter)
        chat_service = ChatService(
            kb_service=kb_service,
            llm_client=rate_limited_llm_client,
            similarity_threshold=settings.similarity_threshold,
        )

        app.state.container = AppContainer(
            settings=settings,
            http_client=http_client,
            kb_service=kb_service,
            llm_client=rate_limited_llm_client,
            chat_service=chat_service,
        )
        try:
            yield
        finally:
            await http_client.aclose()

    app = FastAPI(title="Thoughtful AI Support Agent", version="1.0.0", lifespan=lifespan)

    if FRONTEND_DIST_DIR.exists():
        assets_dir = FRONTEND_DIST_DIR / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            settings.cors_origin,
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/")
    async def index() -> FileResponse:
        if FRONTEND_INDEX_HTML.exists():
            return FileResponse(str(FRONTEND_INDEX_HTML))
        raise HTTPException(status_code=404, detail="Frontend is not built")

    @app.get("/{path:path}")
    async def spa_fallback(path: str) -> FileResponse:
        if path.startswith(("chat", "health", "assets", "docs", "redoc", "openapi.json")):
            raise HTTPException(status_code=404, detail="Not found")
        if FRONTEND_INDEX_HTML.exists():
            return FileResponse(str(FRONTEND_INDEX_HTML))
        raise HTTPException(status_code=404, detail="Frontend is not built")

    @app.post("/chat", response_model=ChatResponse)
    async def chat(
        req: ChatRequest,
        chat_service: ChatService = Depends(get_chat_service),
    ) -> ChatResponse:
        try:
            result = await chat_service.answer(req.message)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except RateLimitExceeded as e:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded for LLM requests",
                headers={"Retry-After": str(e.retry_after_seconds)},
            ) from e
        except LLMConfigurationError as e:
            raise HTTPException(status_code=500, detail=str(e)) from e
        except LLMRequestError as e:
            raise HTTPException(status_code=502, detail=str(e)) from e

        return ChatResponse(
            answer=result.answer,
            source=result.source,
            matched_question=result.matched_question,
            score=result.score,
        )

    return app


app = create_app()

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppSettings:
    kb_path: Path
    similarity_threshold: float
    cors_origin: str

    llm_provider: str
    openai_api_key: str | None
    openai_model: str
    gemini_api_key: str | None
    gemini_model: str


def load_settings() -> AppSettings:
    kb_path = Path(__file__).resolve().parent / "kb.json"

    threshold_raw = os.getenv("SIMILARITY_THRESHOLD")
    similarity_threshold = 0.35
    if threshold_raw:
        try:
            similarity_threshold = float(threshold_raw)
        except ValueError as e:
            raise ValueError("SIMILARITY_THRESHOLD must be a number") from e

    return AppSettings(
        kb_path=kb_path,
        similarity_threshold=similarity_threshold,
        cors_origin=os.getenv("CORS_ORIGIN", "http://localhost:5173"),
        llm_provider=os.getenv("LLM_PROVIDER", "").strip().lower(),
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        gemini_api_key=os.getenv("GEMINI_API_KEY") or None,
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
    )

from __future__ import annotations

from typing import Protocol

from backend.services.kb_service import KBMatch


class KnowledgeBasePort(Protocol):
    async def find_best_match(self, query: str) -> KBMatch | None:
        raise NotImplementedError


class LLMPort(Protocol):
    async def generate(self, prompt: str) -> str:
        raise NotImplementedError

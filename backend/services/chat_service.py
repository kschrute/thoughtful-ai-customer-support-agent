from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from backend.services.exceptions import ValidationError
from backend.services.ports import KnowledgeBasePort, LLMPort


@dataclass(frozen=True)
class ChatResult:
    answer: str
    source: Literal["kb", "llm"]
    matched_question: str | None = None
    score: float | None = None


class ChatService:
    def __init__(
        self,
        kb_service: KnowledgeBasePort,
        llm_client: LLMPort,
        similarity_threshold: float,
    ) -> None:
        self._kb = kb_service
        self._llm = llm_client
        self._threshold = similarity_threshold

    async def answer(self, message: str) -> ChatResult:
        query = message.strip()
        if not query:
            raise ValidationError("message must not be empty")

        match = await self._kb.find_best_match(query)
        if match is not None and match.score >= self._threshold:
            return ChatResult(
                answer=match.answer,
                source="kb",
                matched_question=match.question,
                score=match.score,
            )

        answer = await self._llm.generate(query)
        return ChatResult(answer=answer, source="llm")

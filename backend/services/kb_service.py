from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass(frozen=True)
class KBItem:
    question: str
    answer: str


@dataclass(frozen=True)
class KBMatch:
    question: str
    answer: str
    score: float


class KnowledgeBaseService:
    def __init__(self, items: list[KBItem]) -> None:
        if not items:
            raise ValueError("Knowledge base items must not be empty")
        self._items = items
        self._vectorizer = TfidfVectorizer(stop_words="english")
        self._matrix = self._vectorizer.fit_transform([i.question for i in items])

    @staticmethod
    def from_json(path: Path) -> KnowledgeBaseService:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as e:
            raise RuntimeError(f"KB file not found: {path}") from e
        except json.JSONDecodeError as e:
            raise RuntimeError(f"KB file is not valid JSON: {path}") from e

        questions = raw.get("questions")
        if not isinstance(questions, list):
            raise RuntimeError("KB JSON must contain a 'questions' list")

        items: list[KBItem] = []
        for item in questions:
            if not isinstance(item, dict):
                continue
            q = item.get("question")
            a = item.get("answer")
            if isinstance(q, str) and isinstance(a, str) and q.strip() and a.strip():
                items.append(KBItem(question=q.strip(), answer=a.strip()))

        if not items:
            raise RuntimeError("KB contains no valid question/answer items")

        return KnowledgeBaseService(items)

    async def find_best_match(self, query: str) -> KBMatch | None:
        return await asyncio.to_thread(self._find_best_match_sync, query)

    def _find_best_match_sync(self, query: str) -> KBMatch | None:
        query_clean = query.strip()
        if not query_clean:
            return None

        query_vec = self._vectorizer.transform([query_clean])
        sims = cosine_similarity(query_vec, self._matrix)[0]
        if sims.size == 0:
            return None

        best_idx = int(np.argmax(sims))
        best_score = float(sims[best_idx])
        item = self._items[best_idx]
        return KBMatch(question=item.question, answer=item.answer, score=best_score)

from __future__ import annotations

import asyncio
import time
from collections import deque
from dataclasses import dataclass

from backend.services.exceptions import ServiceError
from backend.services.ports import LLMPort


@dataclass(frozen=True)
class RateLimitExceeded(ServiceError):
    retry_after_seconds: int


class AsyncSlidingWindowRateLimiter:
    def __init__(self, *, max_requests: int, window_seconds: int) -> None:
        if max_requests < 1:
            raise ValueError("max_requests must be >= 1")
        if window_seconds < 1:
            raise ValueError("window_seconds must be >= 1")

        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._lock = asyncio.Lock()
        self._timestamps: deque[float] = deque()

    async def acquire(self) -> None:
        now = time.monotonic()
        async with self._lock:
            window_start = now - self._window_seconds
            while self._timestamps and self._timestamps[0] <= window_start:
                self._timestamps.popleft()

            if len(self._timestamps) < self._max_requests:
                self._timestamps.append(now)
                return

            oldest = self._timestamps[0]
            retry_after = int(max(1.0, (oldest + self._window_seconds) - now))
            raise RateLimitExceeded(retry_after_seconds=retry_after)


class RateLimitedLLMClient:
    def __init__(self, *, llm: LLMPort, limiter: AsyncSlidingWindowRateLimiter) -> None:
        self._llm = llm
        self._limiter = limiter

    async def generate(self, prompt: str) -> str:
        await self._limiter.acquire()
        return await self._llm.generate(prompt)

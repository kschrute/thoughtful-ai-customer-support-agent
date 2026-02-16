from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol

import httpx


SYSTEM_PROMPT = "You are a helpful customer support assistant for Thoughtful AI. Answer concisely."


class LLMClient(Protocol):
    async def generate(self, prompt: str) -> str:
        raise NotImplementedError


class LLMConfigurationError(RuntimeError):
    pass


class LLMRequestError(RuntimeError):
    pass


@dataclass(frozen=True)
class OpenAIConfig:
    api_key: str
    model: str


class OpenAIClient:
    def __init__(self, http_client: httpx.AsyncClient, config: OpenAIConfig) -> None:
        self._http = http_client
        self._config = config

    async def generate(self, prompt: str) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": self._config.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }

        resp = await self._http.post(
            url,
            headers={"Authorization": f"Bearer {self._config.api_key}"},
            json=payload,
        )

        if resp.status_code >= 400:
            raise LLMRequestError(f"OpenAI error {resp.status_code}: {resp.text}")

        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:  # noqa: BLE001
            raise LLMRequestError(f"Unexpected OpenAI response format: {data}") from e


@dataclass(frozen=True)
class GeminiConfig:
    api_key: str
    model: str


class GeminiClient:
    def __init__(self, http_client: httpx.AsyncClient, config: GeminiConfig) -> None:
        self._http = http_client
        self._config = config

    async def generate(self, prompt: str) -> str:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self._config.model}:generateContent"
        )
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{SYSTEM_PROMPT}\n\n{prompt}"}],
                }
            ],
            "generationConfig": {"temperature": 0.2},
        }

        resp = await self._http.post(url, params={"key": self._config.api_key}, json=payload)

        if resp.status_code >= 400:
            raise LLMRequestError(f"Gemini error {resp.status_code}: {resp.text}")

        data = resp.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:  # noqa: BLE001
            raise LLMRequestError(f"Unexpected Gemini response format: {data}") from e


class AutoLLMClient:
    def __init__(
        self,
        http_client: httpx.AsyncClient,
        provider: str,
        openai_api_key: str | None,
        openai_model: str,
        gemini_api_key: str | None,
        gemini_model: str,
    ) -> None:
        self._http = http_client
        self._provider = provider.strip().lower()
        self._openai_api_key = openai_api_key
        self._openai_model = openai_model
        self._gemini_api_key = gemini_api_key
        self._gemini_model = gemini_model

    async def generate(self, prompt: str) -> str:
        provider = self._provider
        if provider == "openai":
            return await self._openai().generate(prompt)
        if provider == "gemini":
            return await self._gemini().generate(prompt)

        if self._openai_api_key:
            return await self._openai().generate(prompt)
        if self._gemini_api_key:
            return await self._gemini().generate(prompt)

        raise LLMConfigurationError(
            "No LLM provider configured. Set OPENAI_API_KEY or GEMINI_API_KEY (or LLM_PROVIDER)."
        )

    def _openai(self) -> OpenAIClient:
        if not self._openai_api_key:
            raise LLMConfigurationError("OPENAI_API_KEY is not set")
        return OpenAIClient(self._http, OpenAIConfig(api_key=self._openai_api_key, model=self._openai_model))

    def _gemini(self) -> GeminiClient:
        if not self._gemini_api_key:
            raise LLMConfigurationError("GEMINI_API_KEY is not set")
        return GeminiClient(self._http, GeminiConfig(api_key=self._gemini_api_key, model=self._gemini_model))


def env_default_timeout_seconds() -> float:
    raw = os.getenv("HTTP_TIMEOUT_SECONDS")
    if not raw:
        return 30.0
    return float(raw)

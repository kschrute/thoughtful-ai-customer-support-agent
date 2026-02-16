from __future__ import annotations

from dataclasses import dataclass

import httpx

from backend.services.chat_service import ChatService
from backend.services.kb_service import KnowledgeBaseService
from backend.services.ports import LLMPort
from backend.settings import AppSettings


@dataclass(frozen=True)
class AppContainer:
    settings: AppSettings
    http_client: httpx.AsyncClient
    kb_service: KnowledgeBaseService
    llm_client: LLMPort
    chat_service: ChatService

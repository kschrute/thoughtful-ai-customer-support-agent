from __future__ import annotations

from fastapi import Request

from backend.container import AppContainer
from backend.services.chat_service import ChatService
from backend.services.exceptions import ServiceError


def get_container(request: Request) -> AppContainer:
    container = getattr(request.app.state, "container", None)
    if not isinstance(container, AppContainer):
        raise RuntimeError("Application container is not initialized")
    return container


def get_chat_service(
    request: Request,
) -> ChatService:
    container = get_container(request)
    chat_service = container.chat_service
    if not isinstance(chat_service, ChatService):
        raise ServiceError("Chat service is not initialized")
    return chat_service

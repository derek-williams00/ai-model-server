"""Abstract base class for LLM providers."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseProvider(ABC):
    """All providers must implement this interface."""

    @abstractmethod
    async def chat_completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Forward a chat completion request and return a response dict."""

    @abstractmethod
    async def completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Forward a text completion request and return a response dict."""

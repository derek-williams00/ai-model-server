"""Ollama provider – forwards requests to a local Ollama instance."""
from __future__ import annotations

import os
from typing import Any

import httpx

from .base import BaseProvider

_DEFAULT_BASE = "http://localhost:11434"


class OllamaProvider(BaseProvider):
    def __init__(self, model: str, api_base: str | None = None) -> None:
        self.model = model
        self.base_url = (api_base or os.environ.get("OLLAMA_BASE_URL", _DEFAULT_BASE)).rstrip("/")

    async def chat_completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        body = dict(payload)
        body["model"] = self.model
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.base_url}/v1/chat/completions",
                json=body,
            )
            resp.raise_for_status()
            return resp.json()

    async def completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        body = dict(payload)
        body["model"] = self.model
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.base_url}/v1/completions",
                json=body,
            )
            resp.raise_for_status()
            return resp.json()

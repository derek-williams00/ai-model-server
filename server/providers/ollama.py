"""Ollama provider – forwards requests to a local Ollama instance."""
from __future__ import annotations

import os
from typing import Any

import httpx

from server.constants import OLLAMA_DEFAULT_BASE_URL, PROVIDER_REQUEST_TIMEOUT
from server.providers.base import BaseProvider


class OllamaProvider(BaseProvider):
    def __init__(self, model: str, api_base: str | None = None) -> None:
        self.model = model
        self.base_url = (api_base or os.environ.get("OLLAMA_BASE_URL", OLLAMA_DEFAULT_BASE_URL)).rstrip("/")

    async def chat_completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        body = dict(payload)
        body["model"] = self.model
        async with httpx.AsyncClient(timeout=PROVIDER_REQUEST_TIMEOUT) as client:
            resp = await client.post(
                f"{self.base_url}/v1/chat/completions",
                json=body,
            )
            resp.raise_for_status()
            return resp.json()

    async def completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        body = dict(payload)
        body["model"] = self.model
        async with httpx.AsyncClient(timeout=PROVIDER_REQUEST_TIMEOUT) as client:
            resp = await client.post(
                f"{self.base_url}/v1/completions",
                json=body,
            )
            resp.raise_for_status()
            return resp.json()

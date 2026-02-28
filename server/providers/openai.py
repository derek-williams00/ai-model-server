"""OpenAI-compatible provider – forwards requests to any OpenAI-style API."""
from __future__ import annotations

import os
from typing import Any

import httpx

from .base import BaseProvider

_DEFAULT_BASE = "https://api.openai.com/v1"


class OpenAIProvider(BaseProvider):
    def __init__(self, model: str, api_base: str | None = None) -> None:
        self.model = model
        self.base_url = (api_base or os.environ.get("OPENAI_API_BASE", _DEFAULT_BASE)).rstrip("/")
        self.api_key = os.environ.get("OPENAI_API_KEY", "")

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def chat_completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        body = dict(payload)
        body["model"] = self.model
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                json=body,
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()

    async def completions(self, payload: dict[str, Any]) -> dict[str, Any]:
        body = dict(payload)
        body["model"] = self.model
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.base_url}/completions",
                json=body,
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()

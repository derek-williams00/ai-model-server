"""Integration tests for the FastAPI application."""
from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from server.config import AppConfig
from server.config.models import ModelConfig, RateLimitConfig
from server.dependencies import get_config, get_rate_limiter
from server.main import app
from server.rate_limiter import RateLimiter


def _make_config(models: dict | None = None) -> AppConfig:
    models = models or {
        "local-small": ModelConfig(provider="ollama", model="llama3"),
        "cloud-large": ModelConfig(provider="openai", model="gpt-4"),
    }
    return AppConfig(models=models)


@pytest.fixture
def client(tmp_path):
    config = _make_config()
    limiter = RateLimiter()
    app.dependency_overrides[get_config] = lambda: config
    app.dependency_overrides[get_rate_limiter] = lambda: limiter
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

def test_dashboard_returns_html(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "AI Model Server" in resp.text
    assert "local-small" in resp.text
    assert "cloud-large" in resp.text


def test_dashboard_path(client):
    resp = client.get("/dashboard")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# GET /v1/models
# ---------------------------------------------------------------------------

def test_list_models(client):
    resp = client.get("/v1/models")
    assert resp.status_code == 200
    data = resp.json()
    assert data["object"] == "list"
    ids = [m["id"] for m in data["data"]]
    assert "local-small" in ids
    assert "cloud-large" in ids


# ---------------------------------------------------------------------------
# POST /v1/chat/completions
# ---------------------------------------------------------------------------

_CHAT_RESPONSE: dict[str, Any] = {
    "id": "chatcmpl-test",
    "object": "chat.completion",
    "choices": [{"message": {"role": "assistant", "content": "Hello!"}, "finish_reason": "stop"}],
    "usage": {"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
}


def test_chat_completions_unknown_model(client):
    resp = client.post("/v1/chat/completions", json={"model": "doesnt-exist", "messages": []})
    assert resp.status_code == 404


def test_chat_completions_success(client):
    with patch("server.api.chat.get_provider") as mock_gp:
        provider = AsyncMock()
        provider.chat_completions = AsyncMock(return_value=_CHAT_RESPONSE)
        mock_gp.return_value = provider
        resp = client.post(
            "/v1/chat/completions",
            json={"model": "local-small", "messages": [{"role": "user", "content": "Hi"}]},
        )
    assert resp.status_code == 200
    assert resp.json()["id"] == "chatcmpl-test"


def test_chat_completions_provider_error(client):
    with patch("server.api.chat.get_provider") as mock_gp:
        provider = AsyncMock()
        provider.chat_completions = AsyncMock(side_effect=Exception("upstream down"))
        mock_gp.return_value = provider
        resp = client.post(
            "/v1/chat/completions",
            json={"model": "local-small", "messages": []},
        )
    assert resp.status_code == 502


# ---------------------------------------------------------------------------
# POST /v1/completions
# ---------------------------------------------------------------------------

_COMPLETION_RESPONSE: dict[str, Any] = {
    "id": "cmpl-test",
    "object": "text_completion",
    "choices": [{"text": "World", "finish_reason": "stop"}],
    "usage": {"prompt_tokens": 2, "completion_tokens": 1, "total_tokens": 3},
}


def test_completions_success(client):
    with patch("server.api.completions.get_provider") as mock_gp:
        provider = AsyncMock()
        provider.completions = AsyncMock(return_value=_COMPLETION_RESPONSE)
        mock_gp.return_value = provider
        resp = client.post(
            "/v1/completions",
            json={"model": "local-small", "prompt": "Hello"},
        )
    assert resp.status_code == 200
    assert resp.json()["id"] == "cmpl-test"


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------

def test_rate_limit_enforced(tmp_path):
    config = _make_config(
        {
            "limited": ModelConfig(
                provider="ollama",
                model="llama3",
                rate_limits=RateLimitConfig(requests_per_minute=1),
            )
        }
    )
    limiter = RateLimiter()
    app.dependency_overrides[get_config] = lambda: config
    app.dependency_overrides[get_rate_limiter] = lambda: limiter
    try:
        with TestClient(app) as c:
            with patch("server.api.chat.get_provider") as mock_gp:
                provider = AsyncMock()
                provider.chat_completions = AsyncMock(return_value=_CHAT_RESPONSE)
                mock_gp.return_value = provider
                # First request should succeed
                r1 = c.post("/v1/chat/completions", json={"model": "limited", "messages": []})
                assert r1.status_code == 200
                # Second request should be rate-limited
                r2 = c.post("/v1/chat/completions", json={"model": "limited", "messages": []})
                assert r2.status_code == 429
    finally:
        app.dependency_overrides.clear()

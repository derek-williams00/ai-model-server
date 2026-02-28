"""Shared completion request handler used by both /v1/chat/completions and /v1/completions."""
from __future__ import annotations

from typing import Any, Awaitable, Callable

from fastapi import HTTPException

from server.config import AppConfig
from server.logging_utils import get_logger, log_error, log_request, log_routing, log_usage
from server.providers import get_provider
from server.providers.base import BaseProvider
from server.rate_limiter import QuotaExceeded, RateLimiter

logger = get_logger(__name__)


async def handle_completion_request(
    payload: dict[str, Any],
    config: AppConfig,
    limiter: RateLimiter,
    endpoint_path: str,
    provider_method: Callable[[BaseProvider], Awaitable[dict[str, Any]]],
) -> dict[str, Any]:
    """Look up the model, enforce rate limits, call the provider, and log usage."""
    alias: str = payload.get("model", "")
    model_cfg = config.models.get(alias)
    if model_cfg is None:
        raise HTTPException(status_code=404, detail=f"Model '{alias}' not found in config")

    log_request(logger, alias, model_cfg.provider, endpoint_path)
    log_routing(logger, alias, model_cfg.provider, model_cfg.model)

    try:
        limiter.check_and_record(alias, model_cfg.rate_limits)
    except QuotaExceeded as exc:
        log_error(logger, alias, str(exc))
        raise HTTPException(status_code=429, detail=str(exc)) from exc

    provider = get_provider(model_cfg)
    try:
        response = await provider_method(provider)
    except Exception as exc:  # noqa: BLE001
        log_error(logger, alias, str(exc))
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    usage = response.get("usage", {})
    total_tokens = usage.get("total_tokens", 0)
    if total_tokens:
        limiter.record_tokens(alias, total_tokens)
    log_usage(logger, alias, usage)
    return response

"""POST /v1/completions endpoint."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from server.config import AppConfig
from server.dependencies import get_config, get_rate_limiter
from server.logging_utils import get_logger, log_error, log_request, log_routing, log_usage
from server.providers import get_provider
from server.rate_limiter import QuotaExceeded, RateLimiter

router = APIRouter()
logger = get_logger(__name__)


@router.post("/v1/completions")
async def completions(
    payload: dict[str, Any],
    config: AppConfig = Depends(get_config),
    limiter: RateLimiter = Depends(get_rate_limiter),
) -> dict[str, Any]:
    alias: str = payload.get("model", "")
    model_cfg = config.models.get(alias)
    if model_cfg is None:
        raise HTTPException(status_code=404, detail=f"Model '{alias}' not found in config")

    log_request(logger, alias, model_cfg.provider, "/v1/completions")
    log_routing(logger, alias, model_cfg.provider, model_cfg.model)

    try:
        limiter.check_and_record(alias, model_cfg.rate_limits)
    except QuotaExceeded as exc:
        log_error(logger, alias, str(exc))
        raise HTTPException(status_code=429, detail=str(exc)) from exc

    provider = get_provider(model_cfg)
    try:
        response = await provider.completions(payload)
    except Exception as exc:  # noqa: BLE001
        log_error(logger, alias, str(exc))
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    usage = response.get("usage", {})
    total_tokens = usage.get("total_tokens", 0)
    if total_tokens:
        limiter.record_tokens(alias, total_tokens)
    log_usage(logger, alias, usage)
    return response

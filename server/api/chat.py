"""POST /v1/chat/completions endpoint."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from server.api.handler import handle_completion_request
from server.config import AppConfig
from server.dependencies import get_config, get_rate_limiter
from server.rate_limiter import RateLimiter

router = APIRouter()


@router.post("/v1/chat/completions")
async def chat_completions(
    payload: dict[str, Any],
    config: AppConfig = Depends(get_config),
    limiter: RateLimiter = Depends(get_rate_limiter),
) -> dict[str, Any]:
    return await handle_completion_request(
        payload=payload,
        config=config,
        limiter=limiter,
        endpoint_path="/v1/chat/completions",
        provider_method=lambda p: p.chat_completions(payload),
    )

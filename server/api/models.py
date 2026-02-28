"""GET /v1/models endpoint."""
from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, Depends

from server.config import AppConfig
from server.dependencies import get_config

router = APIRouter()


@router.get("/v1/models")
async def list_models(config: AppConfig = Depends(get_config)) -> dict[str, Any]:
    """Return models in OpenAI-compatible format."""
    data = [
        {
            "id": alias,
            "object": "model",
            "created": int(time.time()),
            "owned_by": cfg.provider,
        }
        for alias, cfg in config.models.items()
    ]
    return {"object": "list", "data": data}

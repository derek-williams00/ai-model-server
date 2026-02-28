"""Configuration models using Pydantic."""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class RateLimitConfig(BaseModel):
    daily_token_limit: Optional[int] = None
    requests_per_minute: Optional[int] = None


class ModelConfig(BaseModel):
    provider: str
    model: str
    api_base: Optional[str] = None
    rate_limits: Optional[RateLimitConfig] = None


class AppConfig(BaseModel):
    models: dict[str, ModelConfig] = Field(default_factory=dict)
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000

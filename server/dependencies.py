"""Shared FastAPI dependencies."""
from __future__ import annotations

from functools import lru_cache

from server.config import AppConfig, load_config
from server.rate_limiter import RateLimiter


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    return load_config()


@lru_cache(maxsize=1)
def get_rate_limiter() -> RateLimiter:
    return RateLimiter()

"""Structured logging helpers."""
from __future__ import annotations

import logging
import sys
from typing import Any


def setup_logging(level: str = "INFO") -> None:
    """Configure root logger with a structured format."""
    numeric = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        stream=sys.stdout,
        level=numeric,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_request(logger: logging.Logger, model: str, provider: str, endpoint: str) -> None:
    logger.info("request model=%s provider=%s endpoint=%s", model, provider, endpoint)


def log_routing(logger: logging.Logger, alias: str, provider: str, model: str) -> None:
    logger.info("routing alias=%s provider=%s model=%s", alias, provider, model)


def log_usage(logger: logging.Logger, model: str, usage: dict[str, Any]) -> None:
    logger.info(
        "usage model=%s prompt_tokens=%s completion_tokens=%s total_tokens=%s",
        model,
        usage.get("prompt_tokens", 0),
        usage.get("completion_tokens", 0),
        usage.get("total_tokens", 0),
    )


def log_error(logger: logging.Logger, model: str, error: str) -> None:
    logger.error("error model=%s error=%s", model, error)

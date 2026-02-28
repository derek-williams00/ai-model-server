"""Provider factory and registry."""
from __future__ import annotations

from server.config.models import ModelConfig
from server.providers.base import BaseProvider
from server.providers.ollama import OllamaProvider
from server.providers.openai import OpenAIProvider


def get_provider(cfg: ModelConfig) -> BaseProvider:
    """Return a provider instance based on *cfg*."""
    provider_type = cfg.provider.lower()
    if provider_type == "ollama":
        return OllamaProvider(model=cfg.model, api_base=cfg.api_base)
    if provider_type == "openai":
        return OpenAIProvider(model=cfg.model, api_base=cfg.api_base)
    raise ValueError(f"Unknown provider type: {cfg.provider!r}")

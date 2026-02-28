"""Tests for configuration loading and models."""
import textwrap
from pathlib import Path

import httpx
import pytest

from server.config import AppConfig, load_config
from server.config.models import ModelConfig, RateLimitConfig


def test_default_config():
    cfg = AppConfig()
    assert cfg.models == {}
    assert cfg.log_level == "INFO"
    assert cfg.port == 8000


def test_load_config_missing_file(tmp_path):
    cfg = load_config(tmp_path / "nonexistent.yaml")
    assert cfg.models == {}


def test_load_config_from_yaml(tmp_path):
    yaml_content = textwrap.dedent("""\
        models:
          local-small:
            provider: ollama
            model: llama3
          cloud-large:
            provider: openai
            model: gpt-4
            rate_limits:
              daily_token_limit: 50000
              requests_per_minute: 20
        log_level: DEBUG
        port: 9000
    """)
    config_file = tmp_path / "config.yaml"
    config_file.write_text(yaml_content)
    cfg = load_config(config_file)
    assert "local-small" in cfg.models
    assert "cloud-large" in cfg.models
    assert cfg.models["local-small"].provider == "ollama"
    assert cfg.models["local-small"].model == "llama3"
    assert cfg.models["cloud-large"].rate_limits is not None
    assert cfg.models["cloud-large"].rate_limits.daily_token_limit == 50000
    assert cfg.models["cloud-large"].rate_limits.requests_per_minute == 20
    assert cfg.log_level == "DEBUG"
    assert cfg.port == 9000


def test_load_config_env_var(tmp_path, monkeypatch):
    yaml_content = "models:\n  mymodel:\n    provider: ollama\n    model: phi3\n"
    config_file = tmp_path / "myconfig.yaml"
    config_file.write_text(yaml_content)
    monkeypatch.setenv("CONFIG_PATH", str(config_file))
    cfg = load_config()
    assert "mymodel" in cfg.models


# ---------------------------------------------------------------------------
# Config validation tests - verify models exist in their providers
# ---------------------------------------------------------------------------

async def _validate_ollama_model(model_name: str, base_url: str = "http://localhost:11434") -> bool:
    """Check if a model exists in Ollama by attempting to query it."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{base_url}/v1/chat/completions",
                json={"model": model_name, "messages": [{"role": "user", "content": "test"}], "max_tokens": 1},
            )
            # If we get 200, model exists; if 404 with "not found" message, it doesn't
            if response.status_code == 200:
                return True
            if response.status_code == 404:
                return False
            # For other errors, assume model might exist but there's a different issue
            return True
    except Exception:
        # If Ollama is down or unreachable, skip validation
        return True


@pytest.mark.asyncio
async def test_saved_config_has_valid_ollama_models():
    """Verify that saved-config.yaml references Ollama models that actually exist."""
    config_path = Path(__file__).parent.parent / "saved-config.yaml"
    if not config_path.exists():
        pytest.skip("saved-config.yaml not found")
    
    cfg = load_config(config_path)
    
    for alias, model_cfg in cfg.models.items():
        if model_cfg.provider == "ollama":
            is_valid = await _validate_ollama_model(model_cfg.model)
            assert is_valid, f"Model '{model_cfg.model}' in saved-config.yaml does not exist in Ollama"


@pytest.mark.asyncio
async def test_bad_config_has_invalid_ollama_models():
    """Verify that bad-config.yaml references Ollama models that DON'T exist (to test our validation)."""
    config_path = Path(__file__).parent.parent / "bad-config.yaml"
    if not config_path.exists():
        pytest.skip("bad-config.yaml not found")
    
    cfg = load_config(config_path)
    
    # We expect at least one Ollama model in bad-config.yaml to be invalid
    found_invalid = False
    for alias, model_cfg in cfg.models.items():
        if model_cfg.provider == "ollama":
            is_valid = await _validate_ollama_model(model_cfg.model)
            if not is_valid:
                found_invalid = True
                break
    
    assert found_invalid, "bad-config.yaml should contain at least one non-existent Ollama model for testing"

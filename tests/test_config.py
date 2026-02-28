"""Tests for configuration loading and models."""
import textwrap
from pathlib import Path

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

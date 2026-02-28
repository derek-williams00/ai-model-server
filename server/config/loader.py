"""Load and validate YAML configuration."""
from __future__ import annotations

import os
from pathlib import Path

import yaml

from .models import AppConfig

_DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config.yaml"


def load_config(path: str | Path | None = None) -> AppConfig:
    """Load configuration from a YAML file.

    Falls back to ``config.yaml`` in the project root when *path* is not
    supplied.  Environment variable ``CONFIG_PATH`` can also point to the
    file.
    """
    if path is None:
        path = os.environ.get("CONFIG_PATH", str(_DEFAULT_CONFIG_PATH))
    path = Path(path)
    if not path.exists():
        return AppConfig()
    with path.open() as fh:
        raw = yaml.safe_load(fh) or {}
    return AppConfig.model_validate(raw)

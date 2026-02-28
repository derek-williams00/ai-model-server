"""Minimal HTML dashboard for testing and debugging."""
from __future__ import annotations

import html
from pathlib import Path
from string import Template

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from server.config import AppConfig
from server.dependencies import get_config

router = APIRouter()

_TEMPLATE_PATH = Path(__file__).parent / "templates" / "dashboard.html"
_TEMPLATE = Template(_TEMPLATE_PATH.read_text(encoding="utf-8"))


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def dashboard(config: AppConfig = Depends(get_config)) -> HTMLResponse:
    model_rows = "\n      ".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            html.escape(alias), html.escape(cfg.provider), html.escape(cfg.model)
        )
        for alias, cfg in config.models.items()
    ) or "<tr><td colspan=3><em>No models configured</em></td></tr>"

    model_options = "\n      ".join(
        '<option value="{}">{}</option>'.format(html.escape(alias), html.escape(alias))
        for alias in config.models
    ) or '<option value="" disabled selected>No models configured</option>'

    html_content = _TEMPLATE.substitute(model_rows=model_rows, model_options=model_options)
    return HTMLResponse(content=html_content)

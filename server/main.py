"""Main FastAPI application entry point."""
from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI

from server.api import chat_router, completions_router, models_router
from server.dashboard import router as dashboard_router
from server.dependencies import get_config
from server.logging_utils import setup_logging

load_dotenv()

config = get_config()
setup_logging(config.log_level)

app = FastAPI(
    title="AI Model Server",
    description="Lightweight OpenAI-compatible LLM proxy server.",
    version="0.1.0",
)

app.include_router(chat_router)
app.include_router(completions_router)
app.include_router(models_router)
app.include_router(dashboard_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server.main:app",
        host=config.host,
        port=config.port,
        reload=False,
    )

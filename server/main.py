"""Main FastAPI application entry point."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI

from server.api import chat_router, completions_router, models_router
from server.constants import APP_DESCRIPTION, APP_TITLE, APP_VERSION
from server.dashboard import router as dashboard_router
from server.dependencies import get_config
from server.logging_utils import get_logger, setup_logging

load_dotenv()

# Initialise logging before the app starts handling requests.
_startup_config = get_config()
setup_logging(_startup_config.log_level)
_log = get_logger("server.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    cfg = get_config()
    _log.info(
        "AI Model Server starting: host=%s port=%s models=%d",
        cfg.host,
        cfg.port,
        len(cfg.models),
    )
    yield
    _log.info("AI Model Server shutting down")


app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
)

app.include_router(chat_router)
app.include_router(completions_router)
app.include_router(models_router)
app.include_router(dashboard_router)


if __name__ == "__main__":
    import uvicorn

    cfg = get_config()
    uvicorn.run(
        "server.main:app",
        host=cfg.host,
        port=cfg.port,
        workers=1,  # Use gunicorn -w <N> -k uvicorn.workers.UvicornWorker for multi-worker deployments
        access_log=True,
        reload=False,
    )

"""
Main entry point for the application.
"""

import uvicorn
from fastapi import FastAPI
from hayhooks import create_app, log

from .config.settings import settings
from .routes.system import router as system_router


def create_application() -> FastAPI:
    """Creates and configures the FastAPI application."""
    app = create_app()

    log.info("Adding system routes")
    app.include_router(system_router, prefix="/api/v1")
    log.debug("Successfully added System Routes")
    return app


if __name__ == "__main__":
    uvicorn.run(
        "src.main:create_application",
        factory=True,
        host=settings.hayhooks_host,
        port=settings.hayhooks_port,
    )

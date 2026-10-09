"""Application factory for the expense tracker backend API."""

import logging

from fastapi import FastAPI

from app.config import get_settings
from app.core.errors import register_error_handlers
from app.database import create_db_engine, initialize_database
from app.routers.auth import router as auth_router
from app.routers.budgets import router as budgets_router
from app.routers.categories import router as categories_router
from app.routers.dashboard import router as dashboard_router
from app.routers.expenses import router as expenses_router
from app.routers.health import router as health_router

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: The configured application instance.
    """
    application = FastAPI(title="Expense Tracker Dashboard API", version="0.1.0")

    register_error_handlers(application)

    @application.get("/")
    def read_root() -> dict[str, str]:
        """Serve the skeleton root endpoint.

        Returns:
            dict[str, str]: A static status payload.
        """
        return {"status": "ok"}

    application.include_router(health_router)
    application.include_router(auth_router)
    application.include_router(categories_router)
    application.include_router(expenses_router)
    application.include_router(budgets_router)
    application.include_router(dashboard_router)

    @application.on_event("startup")
    def _init_database() -> None:
        """Bind the startup engine and run REQ-BE-131 initialization.

        The engine is created ONLY here (never at import or factory
        time) so bare ``TestClient(create_app())`` tests that never
        trigger startup stay database-free. The primary path logs
        primary initialization through this module logger's `.info`.
        """
        engine = create_db_engine(get_settings().DATABASE_URL)
        application.state.db_engine = engine
        logger.info("startup database initialization (fallback=%s)", engine.url.get_backend_name())
        initialize_database(engine)

    return application


app = create_app()

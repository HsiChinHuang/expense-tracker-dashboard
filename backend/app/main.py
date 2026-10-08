"""Application factory for the expense tracker backend API."""

from fastapi import FastAPI

from app.core.errors import register_error_handlers
from app.routers.auth import router as auth_router
from app.routers.budgets import router as budgets_router
from app.routers.categories import router as categories_router
from app.routers.expenses import router as expenses_router
from app.routers.health import router as health_router


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

    return application


app = create_app()

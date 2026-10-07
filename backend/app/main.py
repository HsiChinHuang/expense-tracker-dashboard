"""Application factory for the expense tracker backend API."""

from fastapi import FastAPI

from app.routers.health import router as health_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: The configured application instance.
    """
    application = FastAPI(title="Expense Tracker Dashboard API", version="0.1.0")

    @application.get("/")
    def read_root() -> dict[str, str]:
        """Serve the skeleton root endpoint.

        Returns:
            dict[str, str]: A static status payload.
        """
        return {"status": "ok"}

    application.include_router(health_router)

    return application


app = create_app()

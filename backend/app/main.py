"""Application factory for the expense tracker backend API.

Single-container serving (REQ-ARCH-071, REQ-BE-140 SPA half, REQ-TECH-042):
when the image has copied the built frontend into ``backend/static`` the
factory additionally mounts the asset directory and an SPA fallback route.
The wiring is gated on ``backend/static/index.html`` existing, so the
committed (route-free) tree and every merged test are unaffected.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.errors import register_error_handlers
from app.routers.auth import router as auth_router
from app.routers.budgets import router as budgets_router
from app.routers.categories import router as categories_router
from app.routers.dashboard import router as dashboard_router
from app.routers.expenses import router as expenses_router
from app.routers.health import router as health_router

SPA_MOUNT_NAME: str = "spa"
SPA_MOUNT_PATH: str = "/assets"
SPA_FALLBACK_PATH: str = "/{requested_path:path}"
SPA_INDEX_FILE: str = "index.html"


def resolve_static_dir() -> Path:
    """Return the directory holding the built frontend assets.

    Returns:
        Path: ``backend/static`` — the exact directory the Dockerfile's
            ``COPY --from=frontend-build /app/frontend/dist ./static``
            leg lands in.
    """
    return Path(__file__).resolve().parent.parent / "static"


def register_spa_static(application: FastAPI, static_dir: Path, index_file: Path) -> None:
    """Mount the built assets and the SPA fallback route on the application.

    Args:
        application: The application to extend.
        static_dir: Directory containing the built frontend.
        index_file: The ``index.html`` served for client-side routes.
    """
    application.mount(
        SPA_MOUNT_PATH, StaticFiles(directory=static_dir, html=True), name=SPA_MOUNT_NAME
    )

    @application.get(SPA_FALLBACK_PATH, include_in_schema=False)
    def serve_spa_frontend(requested_path: str = "") -> FileResponse:
        """Serve a built asset or fall back to the SPA index document.

        Args:
            requested_path: Path below the root, matched by the catch-all.

        Returns:
            FileResponse: The requested asset, else ``index.html``.
        """
        candidate = (static_dir / requested_path).resolve()
        if candidate.is_file() and candidate.is_relative_to(static_dir.resolve()):
            return FileResponse(candidate)
        return FileResponse(index_file)


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

    static_dir = resolve_static_dir()
    index_file = static_dir / SPA_INDEX_FILE
    if index_file.is_file():
        register_spa_static(application, static_dir, index_file)

    return application


app = create_app()

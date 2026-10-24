"""Application factory for the expense tracker backend API.

Single-container serving (REQ-ARCH-071, REQ-BE-140 SPA half, REQ-TECH-042):
when the image has copied the built frontend into ``backend/static`` the
factory additionally mounts the asset directory and an SPA fallback route.
The wiring is gated on ``backend/static/index.html`` existing, so the
committed (route-free) tree and every merged test are unaffected.
"""

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.core.errors import register_error_handlers
from app.database import create_db_engine, initialize_database
from app.routers.auth import router as auth_router
from app.routers.budgets import router as budgets_router
from app.routers.categories import router as categories_router
from app.routers.dashboard import router as dashboard_router
from app.routers.expenses import router as expenses_router
from app.routers.health import router as health_router
from app.telemetry import register_metrics, setup_telemetry
from app.trace import install_trace_correlation

logger = logging.getLogger(__name__)

SPA_MOUNT_NAME: str = "spa"
SPA_MOUNT_PATH: str = "/assets"
SPA_FALLBACK_PATH: str = "/{requested_path:path}"
SPA_INDEX_FILE: str = "index.html"
SPA_ASSET_SUBDIR: str = "assets"


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

    ``static_dir`` is the whole copied dist (``index.html`` at its root
    plus every hashed bundle below ``assets/``), so the mount resolves
    the inner bundle directory: mounting the dist root at ``/assets``
    would make ``/assets/<hashed>.js`` look for the file one level too
    high and 404 every hosted bundle. There is deliberately no
    flat-layout fallback: a dist without ``assets/`` fails at startup
    rather than silently serving a blank page.

    Args:
        application: The application to extend.
        static_dir: Directory containing the built frontend.
        index_file: The ``index.html`` served for client-side routes.
    """
    application.mount(
        SPA_MOUNT_PATH,
        StaticFiles(directory=static_dir / SPA_ASSET_SUBDIR, html=True),
        name=SPA_MOUNT_NAME,
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
    application = FastAPI(title="Expense Tracker Dashboard API", version=get_settings().APP_VERSION)

    register_error_handlers(application)

    # t122 trace correlation (additive wiring, P6): the provider, the
    # one-span-per-request middleware and the handler-level log filter are
    # installed right after the error handlers and BEFORE every route so
    # each request (including the 401 pair the correlation test drives)
    # runs inside a server span whose 32-hex id the access line carries.
    application = install_trace_correlation(application)

    # The decorator, the ``-> dict[str, str]`` annotation, the docstring
    # and the operationId below are FROZEN CONTRACT, not style: openapi.yaml
    # carries this route's summary and description verbatim (leg 227, t59) and
    # the root response model is derived from the annotation, so widening the
    # annotation (or adding response_model=None) regenerates the byte-pinned
    # contract. The annotation is therefore a deliberate lie to mypy-strict on
    # the static-present return, repaired by exactly one type: ignore below.
    @application.get("/")
    def read_root() -> dict[str, str]:
        """Serve the skeleton root endpoint.

        Returns:
            dict[str, str]: A static status payload.
        """
        if index_file.is_file():
            return FileResponse(index_file)  # type: ignore[return-value]
        return {"status": "ok"}

    application.include_router(health_router)
    application.include_router(auth_router)
    application.include_router(categories_router)
    application.include_router(expenses_router)
    application.include_router(budgets_router)
    application.include_router(dashboard_router)

    # t78 metrics substrate (additive wiring, P6): the provider is
    # installed first so the exposition route can serve it, and BOTH
    # entry points run before the SPA catch-all below, or a
    # built-frontend deployment would swallow /metrics into
    # serve_spa_frontend.
    setup_telemetry(application)
    register_metrics(application)

    static_dir = resolve_static_dir()
    index_file = static_dir / SPA_INDEX_FILE
    if index_file.is_file():
        register_spa_static(application, static_dir, index_file)

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

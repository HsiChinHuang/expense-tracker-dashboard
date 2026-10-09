"""Unit tests for the single-container SPA static mount (t24 ac6).

Class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs.

The mount is gated on ``backend/static/index.html`` existing (never
committed — the image copies the built frontend there), so the committed
tree stays route-free and the merged suites are unaffected. Each test
builds its own application and its own temporary static directory; no
file inside ``backend/static`` is created, mutated, or deleted here.
"""

from pathlib import Path

from fastapi.staticfiles import StaticFiles
from fastapi.testclient import TestClient
from starlette.routing import Mount

from app.main import (
    SPA_FALLBACK_PATH,
    SPA_INDEX_FILE,
    SPA_MOUNT_NAME,
    SPA_MOUNT_PATH,
    create_app,
    register_spa_static,
    resolve_static_dir,
)

INDEX_MARKUP = "<!doctype html><html><head><title>SPA</title></head><body>index</body></html>"
ASSET_MARKUP = "console.log('built asset');\n"


def _build_static(tmp_path: Path) -> Path:
    """Create a fake built-frontend directory and return its path.

    Args:
        tmp_path: pytest-provided directory for this test's files.

    Returns:
        Path: Directory carrying an index.html and one hashed asset.
    """
    static_dir = tmp_path / "static"
    (static_dir / "assets").mkdir(parents=True)
    (static_dir / SPA_INDEX_FILE).write_text(INDEX_MARKUP, encoding="utf-8")
    (static_dir / "app.js").write_text(ASSET_MARKUP, encoding="utf-8")
    return static_dir


class TestStaticServing:
    """Contract coverage for the gated StaticFiles mount and SPA fallback."""

    def test_create_app_without_static_dir_registers_no_spa_fallback_route(
        self,
    ) -> None:
        """A tree without a built frontend stays route-free (additive delta)."""
        assert not resolve_static_dir().joinpath(SPA_INDEX_FILE).is_file(), (
            "the build output must never be committed"
        )

        application = create_app()
        paths = [getattr(route, "path", "") for route in application.routes]

        assert not [route for route in application.routes if isinstance(route, Mount)]
        assert SPA_FALLBACK_PATH not in paths
        assert "/*" not in paths
        assert paths.count("/") == 1

        client = TestClient(application)
        assert client.get("/api/v1/health").status_code == 200
        assert client.get("/openapi.json").status_code == 200
        assert client.get("/some/client/route").status_code == 404

    def test_create_app_with_static_dir_mounts_assets_and_serves_index_fallback(
        self, tmp_path: Path
    ) -> None:
        """With a built frontend the assets mount and the fallback serves index."""
        static_dir = _build_static(tmp_path)
        application = create_app()
        register_spa_static(application, static_dir, static_dir / SPA_INDEX_FILE)

        mounts = [route for route in application.routes if isinstance(route, Mount)]
        assert [route.path for route in mounts] == [SPA_MOUNT_PATH]
        assert mounts[0].name == SPA_MOUNT_NAME
        assert isinstance(mounts[0].app, StaticFiles)

        client = TestClient(application)
        asset_response = client.get(f"{SPA_MOUNT_PATH}/app.js")
        assert asset_response.status_code == 200
        assert asset_response.text == ASSET_MARKUP

        fallback = client.get("/dashboard/monthly")
        assert fallback.status_code == 200
        assert "index" in fallback.text

        assert client.get("/api/v1/health").status_code == 200

    def test_spa_fallback_route_is_excluded_from_the_openapi_schema(
        self, tmp_path: Path
    ) -> None:
        """The catch-all never leaks into the public OpenAPI contract."""
        static_dir = _build_static(tmp_path)
        application = create_app()
        register_spa_static(application, static_dir, static_dir / SPA_INDEX_FILE)

        schema = application.openapi()

        assert SPA_FALLBACK_PATH not in schema["paths"]
        assert not [path for path in schema["paths"] if path.endswith("path}")]
        assert "/api/v1/health" in schema["paths"]

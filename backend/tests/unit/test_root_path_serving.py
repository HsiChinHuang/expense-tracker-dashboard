"""Unit tests for the root path serving the built SPA (t110 ac2).

The hosted defect (D2): ``create_app`` registered the JSON status handler
at ``GET /`` unconditionally, so an operator opening the bare deployed
URL received ``{"status": "ok"}`` instead of the application. The ruling
recorded on the card is a scoping, not a replacement: with a built
frontend present the ONE existing root route returns the built index
document; on the route-free committed tree it keeps returning the JSON
status payload that the frozen t1 smoke contract pins.

Each test builds its own application and its own temporary Vite-shaped
static tree (``index.html`` at the static root, hashed bundles below
``assets/``) and reaches ``create_app()`` through the module's own
``resolve_static_dir`` seam, so production's wiring path is what runs.
Nothing inside ``backend/static`` is created, mutated, or deleted here.

Class and function names are part of the issue contract: the AC
verification commands reference this file's pytest node IDs.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from starlette.routing import Mount
from starlette.testclient import TestClient

from app import main as spa_main
from app.main import (
    SPA_ASSET_SUBDIR,
    SPA_INDEX_FILE,
    SPA_MOUNT_PATH,
    create_app,
)

INDEX_HASH = "b1t110rootpath00000000"
INDEX_MARKUP = (
    '<!doctype html><html lang="en"><head>'
    f'<link rel="stylesheet" href="/{SPA_ASSET_SUBDIR}/index-{INDEX_HASH}.css">'
    f'<script type="module" src="/{SPA_ASSET_SUBDIR}/index-{INDEX_HASH}.js"></script>'
    "</head><body><div id=\"root\"></div></body></html>\n"
)
BUNDLE_MARKUP = f'console.log("hermetic built bundle for t110 {INDEX_HASH}");\n'
STYLE_MARKUP = "body{color:#000}\n"


def _build_vite_shaped_static(tmp_path: Path) -> Path:
    """Create a Vite-shaped built-frontend directory and return its path.

    The layout mirrors ``frontend/dist`` as the image ships it: the index
    document at the static root naming hashed bundles below ``assets/``.

    Args:
        tmp_path: pytest-provided directory for this test's files.

    Returns:
        Path: Directory carrying ``index.html`` at the root plus one
            hashed ``.js`` and one hashed ``.css`` below ``assets/``.
    """
    static_dir = tmp_path / "static"
    (static_dir / SPA_ASSET_SUBDIR).mkdir(parents=True)
    (static_dir / SPA_INDEX_FILE).write_text(INDEX_MARKUP, encoding="utf-8")
    bundle_dir = static_dir / SPA_ASSET_SUBDIR
    (bundle_dir / f"index-{INDEX_HASH}.js").write_text(BUNDLE_MARKUP, encoding="utf-8")
    (bundle_dir / f"index-{INDEX_HASH}.css").write_text(STYLE_MARKUP, encoding="utf-8")
    return static_dir


@pytest.fixture
def staged_static_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """Patch ``resolve_static_dir`` to a staged tree and restore it after.

    The patch is applied to the module attribute the factory itself calls,
    so ``create_app()`` wires the production code path against the staged
    directory without anything being written inside ``backend/static``.

    Args:
        tmp_path: pytest-provided directory for this test's files.
        monkeypatch: pytest monkeypatch fixture for the module seam.

    Yields:
        Iterator[Path]: The staged Vite-shaped static directory.
    """
    static_dir = _build_vite_shaped_static(tmp_path)
    monkeypatch.setattr(spa_main, "resolve_static_dir", lambda: static_dir)
    yield static_dir


class TestRootPathServing:
    """Contract coverage for the root route returning the built SPA document."""

    def test_root_serves_spa_document_with_built_frontend_present(
        self, staged_static_dir: Path
    ) -> None:
        """With a built frontend, GET / answers 200 text/html with the index document."""
        assert (staged_static_dir / SPA_INDEX_FILE).is_file()
        assert spa_main.resolve_static_dir() == staged_static_dir, "the seam must reach the factory"

        client = TestClient(create_app())
        response = client.get("/")

        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert 'id="root"' in response.text

    def test_root_serves_spa_whose_named_bundle_resolves_on_the_same_app(
        self, staged_static_dir: Path
    ) -> None:
        """The composite holds: the document at / and the bundle it names both answer."""
        client = TestClient(create_app())

        document = client.get("/")
        bundle = client.get(f"{SPA_MOUNT_PATH}/index-{INDEX_HASH}.js")
        style = client.get(f"{SPA_MOUNT_PATH}/index-{INDEX_HASH}.css")

        assert f'src="/{SPA_ASSET_SUBDIR}/index-{INDEX_HASH}.js"' in document.text
        assert bundle.status_code == 200
        assert "text/javascript" in bundle.headers.get("content-type", "")
        assert bundle.text == BUNDLE_MARKUP
        assert style.status_code == 200

    def test_root_fix_keeps_single_asset_mount_and_api_routes(
        self, staged_static_dir: Path
    ) -> None:
        """The root change does not re-wire the mount or swallow the API surface."""
        application = create_app()
        mounts = [route for route in application.routes if isinstance(route, Mount)]

        assert [route.path for route in mounts] == [SPA_MOUNT_PATH]

        client = TestClient(application)
        assert client.get("/api/v1/health").status_code == 200
        assert client.get("/openapi.json").status_code == 200

    def test_root_keeps_json_status_payload_on_route_free_tree(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Without a built frontend the one root route still returns the status dict.

        The empty static directory is staged rather than assumed, so this leg
        measures the route-free branch of the handler under any ambient static
        tree (the ac2 fence injects one process-wide via ``sitecustomize``).
        """
        committed_static = Path(spa_main.__file__).resolve().parent.parent / "static"
        assert not (committed_static / SPA_INDEX_FILE).is_file(), (
            "the build output must never be committed - it is what makes the "
            "committed tree route-free"
        )
        empty_static = tmp_path / "empty-static"
        empty_static.mkdir()
        monkeypatch.setattr(spa_main, "resolve_static_dir", lambda: empty_static)

        application = create_app()
        paths = [getattr(route, "path", "") for route in application.routes]
        client = TestClient(application)
        response = client.get("/")

        assert paths.count("/") == 1, "the root must stay exactly one route"
        assert not [route for route in application.routes if isinstance(route, Mount)]
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        assert client.get("/api/v1/health").status_code == 200
        assert client.get("/some/client/route").status_code == 404

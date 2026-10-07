"""Smoke tests proving the skeleton application boots and answers GET /."""

from fastapi.testclient import TestClient

from app.main import app, create_app


class TestSmoke:
    """Skeleton-level smoke coverage for the application factory."""

    def test_root_returns_200(self) -> None:
        """GET / on a freshly created app returns HTTP 200."""
        client = TestClient(create_app())

        response = client.get("/")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_module_app_is_factory_created(self) -> None:
        """The module-level app is a FastAPI instance built by create_app."""
        client = TestClient(app)

        response = client.get("/")

        assert response.status_code == 200

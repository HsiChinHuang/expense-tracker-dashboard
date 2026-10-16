"""Unit tests for the OTel metrics substrate (t78).

Class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs.

The five pinned nodes cover: substrate installation and idempotency
(ac1), the loopback-admitted exposition carrying the three pinned
resource attributes (ac2), the non-loopback refusal (ac3), the
development-only mount (ac3), and the OpenAPI schema absence (ac4).
``TestClient``'s default peer is the non-IP ``("testclient", 50000)``,
so every admission test passes an explicit ``client=("127.0.0.1", N)``
and the refusal test relies on that default on purpose.
"""

import logging

import pytest
from fastapi.testclient import TestClient
from opentelemetry.metrics import Meter, get_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from starlette.requests import Request
from starlette.routing import Route

from app.config import get_settings
from app.main import SPA_FALLBACK_PATH, create_app
from app.telemetry import (
    SERVICE_NAME,
    SUBSTRATE_METER_SCOPE,
    exposition_body,
    get_meter,
    is_loopback_peer,
    setup_telemetry,
)

LOOPBACK_CLIENT: tuple[str, int] = ("127.0.0.1", 5053)
FORGED_XFF: dict[str, str] = {"X-Forwarded-For": "127.0.0.1"}
PRODUCTION_SECRET = "cyphress-test-secret-key-32-chars-longer"


def _route_paths(application: object) -> list[str]:
    """Return the declared route paths of an application.

    Args:
        application: The application under test (a FastAPI instance).

    Returns:
        list[str]: Every route path, schema-hidden routes included.
    """
    routes = getattr(application, "routes", [])
    return [str(route.path) for route in routes if isinstance(route, Route)]


def _peer_request(host: str) -> Request:
    """Build a minimal request whose direct ASGI peer is ``host``.

    Args:
        host: The peer address the loopback gate should inspect.

    Returns:
        Request: A scope-carrying request with ``client = (host, 5053)``.
    """
    return Request({"type": "http", "client": (host, 5053)})


class TestTelemetrySubstrate:
    """Contract coverage for the provider installation (ac1)."""

    def test_setup_telemetry_installs_a_meter_provider_once(
        self,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """A second setup call keeps the first provider and stays silent.

        ``create_app()`` runs once at import and again per test
        application, so the guard in ``setup_telemetry`` must return
        before ``set_meter_provider``; the SDK's own
        ``Overriding of current MeterProvider`` warning appearing in this
        run's output is the failure mode this node fences.
        """
        installed = get_meter_provider()
        assert isinstance(installed, MeterProvider), (
            "create_app() must have installed the SDK meter provider"
        )

        with caplog.at_level(logging.WARNING):
            setup_telemetry(create_app())
            setup_telemetry(create_app())

        assert get_meter_provider() is installed, (
            "the second setup call must keep the first provider, not swap it"
        )
        assert "Overriding of current MeterProvider" not in caplog.text

        meter = get_meter(SUBSTRATE_METER_SCOPE)
        assert isinstance(meter, Meter)
        body = exposition_body()
        assert b"target_info" in body, "the reader must expose the resource identity"
        assert b"process_uptime" in body, "the substrate instrument must reach the exposition"


class TestMetricsEndpoint:
    """Contract coverage for the loopback-gated exposition (ac2/ac3/ac4)."""

    def test_metrics_endpoint_returns_200_with_the_three_resource_attributes(
        self,
    ) -> None:
        """A loopback peer scrapes 200 with target_info bearing all three values."""
        client = TestClient(create_app(), client=LOOPBACK_CLIENT)

        response = client.get("/metrics")

        assert response.status_code == 200
        body = response.text
        assert f'service_name="{SERVICE_NAME}"' in body
        assert 'deployment_environment="development"' in body
        assert 'service_version="1.0.0"' in body
        assert "target_info" in body
        samples = [line for line in body.splitlines() if line and not line.startswith("#")]
        assert len(samples) >= 1, "an empty 200 proves nothing; a sample line must be live"
        assert response.headers["content-type"].startswith("text/plain")
        assert b"target_info" in exposition_body(), (
            "the route and the module expose the same registry"
        )

    def test_metrics_endpoint_is_404_for_a_non_loopback_client(
        self,
    ) -> None:
        """A refused peer sees the unknown-path 404, forged XFF or not."""
        refused = TestClient(create_app())

        assert refused.get("/metrics").status_code == 404, (
            "the TestClient default peer 'testclient' is not loopback and must be refused"
        )
        assert refused.get("/metrics").json() == {"detail": "Not Found"}

        forged = TestClient(create_app(), headers=FORGED_XFF)
        assert forged.get("/metrics").status_code == 404, (
            "the gate reads the direct ASGI peer only; X-Forwarded-For is never consulted"
        )

        assert refused.get("/api/v1/health").status_code == 200, (
            "the 404 is endpoint-specific, not a middleware kill switch"
        )

    def test_metrics_endpoint_is_absent_from_the_openapi_document(
        self,
    ) -> None:
        """The route stays out of the schema so the frozen contract stays parity-clean."""
        application = create_app()

        paths = application.openapi()["paths"]

        assert not [path for path in paths if "metrics" in path], (
            "/metrics must be registered with include_in_schema=False"
        )
        assert "/api/v1/health" in paths
        declared = _route_paths(application)
        assert "/metrics" in declared, "the route exists; only the schema hides it"
        if SPA_FALLBACK_PATH in declared:
            assert declared.index("/metrics") < declared.index(SPA_FALLBACK_PATH), (
                "the metrics route must register before the SPA catch-all"
            )


class TestTelemetryWiring:
    """Contract coverage for the environment gate (ac3)."""

    def test_metrics_endpoint_is_mounted_in_development_and_absent_in_production(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """One process builds both apps: development serves 200, production 404."""
        assert get_settings().ENVIRONMENT == "development"
        development = TestClient(create_app(), client=LOOPBACK_CLIENT)
        assert development.get("/metrics").status_code == 200

        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("JWT_SECRET", PRODUCTION_SECRET)
        get_settings.cache_clear()
        try:
            production_app = create_app()
            production = TestClient(production_app, client=LOOPBACK_CLIENT)

            assert production.get("/metrics").status_code == 404, (
                "a production-configured app does not carry the route at all"
            )
            assert "/metrics" not in _route_paths(production_app)
            assert production.get("/api/v1/health").status_code == 200
        finally:
            monkeypatch.undo()
            get_settings.cache_clear()

        assert is_loopback_peer(_peer_request("127.0.0.1"))
        assert is_loopback_peer(_peer_request("::1"))
        assert not is_loopback_peer(_peer_request("203.0.113.9"))
        assert not is_loopback_peer(_peer_request("testclient"))

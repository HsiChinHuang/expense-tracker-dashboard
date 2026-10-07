"""Integration tests for the public health check endpoint (t3).

Test class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs.
"""

from fastapi.testclient import TestClient

from app.main import create_app

EXPECTED_FIELDS = {"status", "database", "fallback_active", "version"}


class TestHealthApi:
    """Contract coverage for GET /api/v1/health."""

    def test_health_returns_200_without_auth(self) -> None:
        """GET /api/v1/health is public and answers 200 with no header."""
        client = TestClient(create_app())

        response = client.get("/api/v1/health")

        assert response.status_code == 200

    def test_health_body_has_exactly_four_fields(self) -> None:
        """The JSON body keys are exactly the four documented fields."""
        client = TestClient(create_app())

        response = client.get("/api/v1/health")

        assert set(response.json().keys()) == EXPECTED_FIELDS

    def test_health_response_matches_pydantic_schema(self) -> None:
        """Values stay in the documented domains and OpenAPI marks the
        four fields as required (schema-backed route, not a bare dict)."""
        application = create_app()
        client = TestClient(application)

        body = client.get("/api/v1/health").json()

        assert body["status"] in {"ok", "degraded"}
        assert body["database"] in {"postgresql", "sqlite"}
        assert isinstance(body["fallback_active"], bool)
        assert isinstance(body["version"], str)

        schema = application.openapi()
        health_path = schema["paths"]["/api/v1/health"]["get"]
        response_schema = health_path["responses"]["200"]["content"][
            "application/json"
        ]["schema"]
        if "$ref" in response_schema:
            component_name = response_schema["$ref"].rsplit("/", 1)[-1]
            response_schema = schema["components"]["schemas"][component_name]
        component = response_schema

        assert set(component["properties"].keys()) == EXPECTED_FIELDS
        assert set(component["required"]) == EXPECTED_FIELDS

    def test_health_phase1_reports_ok_no_fallback(self) -> None:
        """Phase-1 honest reporting: ok, no fallback, configured DB, 0.1.0."""
        application = create_app()
        client = TestClient(application)

        body = client.get("/api/v1/health").json()

        assert body["fallback_active"] is False
        assert body["status"] == "ok"
        assert body["database"] in {"postgresql", "sqlite"}
        assert body["version"] == application.version
        assert (body["status"] == "ok") is (body["fallback_active"] is False)

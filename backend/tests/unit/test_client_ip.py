"""Unit tests for get_client_ip (t12 ac4, REQ-BE-042).

Class and function names are part of the issue contract. The function
is exercised through a minimal FastAPI TestClient route (no database):
the pinned TestClient host is ``testclient``, which is what
``request.client.host`` reports. Chapter 6 6.5.4's frozen rule: truthy
X-Forwarded-For -> first hop stripped; else the direct host.
"""

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.auth.dependencies import get_client_ip

app = FastAPI()


@app.get("/ip-probe")
def ip_probe(request: Request) -> dict[str, str | None]:
    """Return get_client_ip's value for the current request."""
    return {"ip": get_client_ip(request)}


client = TestClient(app)


class TestGetClientIp:
    """Frozen Chapter 6 6.5.4 behavior (t12 ac4)."""

    def test_x_forwarded_for_first_hop_is_returned_and_stripped(self) -> None:
        """Multi-hop and padded single-hop headers yield the first hop."""
        multi = client.get("/ip-probe", headers={"X-Forwarded-For": "203.0.113.5, 70.41.3.18"})
        assert multi.status_code == 200
        assert multi.json()["ip"] == "203.0.113.5"

        padded = client.get("/ip-probe", headers={"X-Forwarded-For": " 203.0.113.5 "})
        assert padded.status_code == 200
        assert padded.json()["ip"] == "203.0.113.5"

    def test_direct_client_host_when_header_absent(self) -> None:
        """No header: request.client.host is returned (TestClient host)."""
        response = client.get("/ip-probe")
        assert response.status_code == 200
        assert response.json()["ip"] == "testclient"

    def test_empty_header_falls_back_to_client_host(self) -> None:
        """An empty X-Forwarded-For value is falsy and falls through."""
        response = client.get("/ip-probe", headers={"X-Forwarded-For": ""})
        assert response.status_code == 200
        assert response.json()["ip"] == "testclient"

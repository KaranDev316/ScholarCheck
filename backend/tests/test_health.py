"""T01: the app starts and answers a health check."""

from fastapi.testclient import TestClient


def test_t01_health_returns_ok(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "scholarcheck-api",
        "environment": "test",
    }


def test_t01_health_accepts_cross_origin_read(client: TestClient) -> None:
    response = client.get(
        "/api/health", headers={"Origin": "http://localhost:5173"}
    )

    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_t01_unknown_route_uses_the_error_body(client: TestClient) -> None:
    response = client.get("/api/does-not-exist")

    assert response.status_code == 404
    body = response.json()
    assert body["code"] == "not_found"
    assert body["message"] == "We could not find that page."
    assert "detail" not in body


def test_t01_openapi_document_is_exposed(client: TestClient) -> None:
    response = client.get("/api/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "ScholarCheck API"

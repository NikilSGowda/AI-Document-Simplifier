from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_frontend_entry_point_is_served() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "AI Smart Document Simplifier" in response.text


def test_frontend_assets_are_served() -> None:
    response = client.get("/app.js")

    assert response.status_code == 200
    assert "/api/health" in response.text


def test_local_frontend_origin_is_allowed() -> None:
    response = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:5500",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5500"

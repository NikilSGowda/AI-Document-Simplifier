from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.text_processor import MAX_TEXT_LENGTH


client = TestClient(app)


def test_simplify_text_returns_explicit_demo_result() -> None:
    response = client.post(
        "/api/simplify-text",
        json={"text": "  A complex instruction.  "},
    )

    assert response.status_code == 200
    assert response.json() == {
        "result_text": "A complex instruction.",
        "processor": "demo_echo",
        "ai_configured": False,
        "notice": (
            "Demonstration only: no AI provider is configured. "
            "The text is returned unchanged apart from trimming outer whitespace; "
            "it has not been simplified."
        ),
    }


def test_simplify_text_rejects_empty_or_whitespace_only_input() -> None:
    for text in ("", " \n\t "):
        response = client.post("/api/simplify-text", json={"text": text})

        assert response.status_code == 400
        assert response.json()["detail"] == "Text must not be empty."


def test_simplify_text_rejects_invalid_request_body() -> None:
    response = client.post("/api/simplify-text", json={"text": 42})

    assert response.status_code == 422


def test_simplify_text_rejects_input_over_maximum_length() -> None:
    response = client.post(
        "/api/simplify-text",
        json={"text": "x" * (MAX_TEXT_LENGTH + 1)},
    )

    assert response.status_code == 422


def test_simplify_text_accepts_input_at_maximum_length() -> None:
    response = client.post(
        "/api/simplify-text",
        json={"text": "x" * MAX_TEXT_LENGTH},
    )

    assert response.status_code == 200
    assert len(response.json()["result_text"]) == MAX_TEXT_LENGTH


def test_local_frontend_origin_can_post() -> None:
    response = client.options(
        "/api/simplify-text",
        headers={
            "Origin": "http://localhost:5500",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5500"

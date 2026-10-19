from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_example_post():
    response = client.post("/example", json={"name": "Wes", "message": "hi"})
    assert response.status_code == 200
    assert response.json() == {
        "received": {"name": "Wes", "message": "hi"},
        "reply": "Hello Wes, you said: hi",
    }


def test_example_post_missing_field():
    response = client.post("/example", json={"name": "Wes"})
    assert response.status_code == 422

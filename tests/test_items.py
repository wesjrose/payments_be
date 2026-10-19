from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_get_item():
    response = client.post("/items", json={"name": "Widget", "price": 9.99})
    assert response.status_code == 201
    item = response.json()
    assert item["name"] == "Widget"

    response = client.get(f"/items/{item['id']}")
    assert response.status_code == 200
    assert response.json() == item

    response = client.get("/items")
    assert item in response.json()


def test_get_missing_item():
    response = client.get("/items/999999")
    assert response.status_code == 404


def test_create_item_validation():
    response = client.post("/items", json={"name": "", "price": -1})
    assert response.status_code == 422

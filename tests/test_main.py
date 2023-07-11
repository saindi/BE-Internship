from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    data = {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == data

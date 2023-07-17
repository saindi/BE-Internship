from httpx import AsyncClient


async def test_health(ac: AsyncClient):
    data = {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }
    response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == data

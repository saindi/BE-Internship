from httpx import AsyncClient

from fastapi import status


async def test_health(ac: AsyncClient):
    data = {
        "status_code": status.HTTP_200_OK,
        "detail": "ok",
        "result": "working"
    }
    response = await ac.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == data

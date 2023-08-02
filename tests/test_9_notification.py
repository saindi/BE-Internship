from httpx import AsyncClient

from fastapi import status


async def test_user_global_rating_analytic(ac: AsyncClient, user_token: dict):
    response = await ac.get("/user/1/global_rating_analytic/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert round(response.json()['rating'], 3) == 0.667

from httpx import AsyncClient

from fastapi import status


async def test_user_get_results(ac: AsyncClient, user_token: dict):
    response = await ac.get("/user/test_results/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 6


async def test_user_get_result_by_id(ac: AsyncClient, user_token: dict):
    response = await ac.get("/user/test_result/1/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()['questions']) == 2


async def test_company_get_results(ac: AsyncClient, user_token: dict):
    response = await ac.get("/company/1/results/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 4


async def test_company_get_results_user(ac: AsyncClient, user_token: dict):
    response = await ac.get("/company/1/results_user/1/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 4


async def test_company_get_results_bad(ac: AsyncClient, user_token: dict):
    response = await ac.get("/company/1/results_user/2/", headers=user_token)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == 'Results not found'


async def test_company_get_results_quiz(ac: AsyncClient, user_token: dict):
    response = await ac.get("/company/1/results_quiz/2/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 4


async def test_company_get_results_quiz_bad(ac: AsyncClient, user_token: dict):
    response = await ac.get("/company/1/results_quiz/3/", headers=user_token)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == 'Results not found'
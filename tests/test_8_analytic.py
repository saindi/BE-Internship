from httpx import AsyncClient

from fastapi import status


async def test_user_global_rating_analytic(ac: AsyncClient, user_token: dict):
    response = await ac.get("/user/1/global_rating_analytic/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert round(response.json()['rating'], 3) == 0.667


async def test_user_quiz_analytic_2(ac: AsyncClient, user_token: dict):
    response = await ac.get("/user/1/quiz_analytic/2/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]['rating'] == 0.75


async def test_user_quiz_analytic_3(ac: AsyncClient, user_token: dict):
    response = await ac.get("/user/1/quiz_analytic/3/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]['rating'] == 0.5


async def test_user_last_pass_quizzes(ac: AsyncClient, user_token: dict):
    response = await ac.get("/user/1/last_pass_quizzes/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
    assert response.json()[0]['id_quiz'] == 2
    assert response.json()[1]['id_quiz'] == 3


async def test_company_users_analytic(ac: AsyncClient, user_token: dict):
    response = await ac.get("/company/1/users_analytic/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]['rating'] == 0.75


async def test_company_user_1_analytic(ac: AsyncClient, user_token: dict):
    response = await ac.get("/company/1/user_analytic/1/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]['rating'] == 0.75


async def test_company_users_last_pass_quizzes(ac: AsyncClient, user_token: dict):
    response = await ac.get("/company/1/last_pass_quizzes/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]['id_user'] == 1

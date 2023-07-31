from httpx import AsyncClient

from fastapi import status

answers = {
    "answers": [
        [0, 1], [1, 0]
    ]
}


async def test_pass_qiuz(ac: AsyncClient, user_token: dict):
    response_1 = await ac.post("/quiz/2/pass_test/", json={
        "answers": [
            [0], [0, 1]
        ]
    }, headers=user_token)

    response_2 = await ac.post("/quiz/2/pass_test/", json={
        "answers": [
            [0], [0]
        ]
    }, headers=user_token)

    response_3 = await ac.post("/quiz/3/pass_test/", json={
        "answers": [
            [1], [1, 0]
        ]
    }, headers=user_token)

    assert response_1.status_code == status.HTTP_201_CREATED
    assert response_1.json()["count_correct_answers"] == 2

    assert response_2.status_code == status.HTTP_201_CREATED
    assert response_2.json()["count_correct_answers"] == 1

    assert response_3.status_code == status.HTTP_201_CREATED
    assert response_3.json()["count_correct_answers"] == 1


async def test_company_rating(ac: AsyncClient, user_token: dict):
    response = await ac.get("/user/company_rating/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
    assert response.json()[0]['rating'] == 0.75
    assert response.json()[1]['rating'] == 0.5


async def test_global_rating(ac: AsyncClient, user_token: dict):
    response = await ac.get("/user/global_rating/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert round(response.json()['rating'], 3) == 0.667

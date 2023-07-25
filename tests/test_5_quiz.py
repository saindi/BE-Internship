from httpx import AsyncClient

from fastapi import status

quiz = {
    "name": "string",
    "description": "string",
    "count_day": 1,
    "questions": [
        {
            "question": "string",
            "answers": [
                {
                    "answer": "string",
                    "is_correct": True
                },
                {
                    "answer": "string",
                    "is_correct": False
                }
            ]
        },
        {
            "question": "string",
            "answers": [
                {
                    "answer": "string",
                    "is_correct": True
                },
                {
                    "answer": "string",
                    "is_correct": True
                }
            ]
        }
    ]
}


async def test_create(ac: AsyncClient, user_token: dict):
    response = await ac.post("/quiz/1/", json=quiz, headers=user_token)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()['id'] == 1


async def test_get_all(ac: AsyncClient, user_token: dict):
    response = await ac.get("/quiz/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


async def test_get_by_id(ac: AsyncClient, user_token: dict):
    response = await ac.get("/quiz/1/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['name'] == 'string'


async def test_update_quiz_info(ac: AsyncClient, user_token: dict):
    response = await ac.put("/quiz/1/update_info/", json={
        "name": "new",
        "description": "new",
        "count_day": 100
    }, headers=user_token)

    response_get = await ac.get("/quiz/1/", headers=user_token)

    assert response.status_code == status.HTTP_201_CREATED
    assert response_get.status_code == status.HTTP_200_OK
    assert response_get.json()['name'] == "new"


async def test_add_question(ac: AsyncClient, user_token: dict):
    response = await ac.post("/quiz/1/add_question/", json={
        "question": "new",
        "answers": [
            {
                "answer": "new",
                "is_correct": True
            },
            {
                "answer": "new",
                "is_correct": False
            },
        ]}, headers=user_token)

    response_get = await ac.get("/quiz/1/", headers=user_token)

    assert response.status_code == status.HTTP_201_CREATED

    assert response_get.status_code == status.HTTP_200_OK
    assert len(response_get.json()['questions']) == 3


async def test_update_question(ac: AsyncClient, user_token: dict):
    response = await ac.put("/question/3/", json={
        "question": "update",
        "answers": [
            {
                "answer": "update",
                "is_correct": False
            },
            {
                "answer": "update",
                "is_correct": True
            },
        ]}, headers=user_token)

    response_get = await ac.get("/quiz/1/", headers=user_token)

    assert response.status_code == status.HTTP_201_CREATED
    assert response_get.status_code == status.HTTP_200_OK


async def test_delete_question(ac: AsyncClient, user_token: dict):
    response = await ac.delete("/question/3/", headers=user_token)

    response_get = await ac.get("/quiz/1/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert response_get.status_code == status.HTTP_200_OK
    assert len(response_get.json()['questions']) == 2


async def test_delete_quiz(ac: AsyncClient, user_token: dict):
    response = await ac.delete("/quiz/1/", params={'quiz_id': 1}, headers=user_token)

    response_all = await ac.get("/quiz/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert response_all.status_code == status.HTTP_400_BAD_REQUEST
    assert response_all.json()['detail'] == "No such quizzes"

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


async def test_create_2(ac: AsyncClient, user_token: dict):
    response_1 = await ac.post("/quiz/1/", json=quiz, headers=user_token)
    response_2 = await ac.post("/quiz/3/", json=quiz, headers=user_token)

    assert response_1.status_code == status.HTTP_201_CREATED
    assert response_1.json()['id'] == 2
    assert response_2.status_code == status.HTTP_201_CREATED
    assert response_2.json()['id'] == 3


async def test_pass_qiuz_bad_answer(ac: AsyncClient, user_token: dict):
    response_few_answers = await ac.post("/quiz/2/pass_test/", json={
        "answers": [
            [0],
        ]
    }, headers=user_token)

    response_many_answers = await ac.post("/quiz/2/pass_test/", json={
        "answers": [
            [0], [0, 1], [0, 1]
        ]
    }, headers=user_token)

    response_same_answers = await ac.post("/quiz/2/pass_test/", json={
        "answers": [
            [0, 1, 1], [0, 1]
        ]
    }, headers=user_token)

    response_no_answer_2 = await ac.post("/quiz/2/pass_test/", json={
        "answers": [
            [0, 2], [0, 1]
        ]
    }, headers=user_token)

    response_bad_index = await ac.post("/quiz/2/pass_test/", json={
        "answers": [
            [0, -1], [0, 1]
        ]
    }, headers=user_token)

    response_empty_answer = await ac.post("/quiz/2/pass_test/", json={
        "answers": [
            [], [0, 1]
        ]
    }, headers=user_token)

    assert response_few_answers.status_code == status.HTTP_400_BAD_REQUEST
    assert response_many_answers.status_code == status.HTTP_400_BAD_REQUEST
    assert response_same_answers.status_code == status.HTTP_400_BAD_REQUEST
    assert response_no_answer_2.status_code == status.HTTP_400_BAD_REQUEST
    assert response_bad_index.status_code == status.HTTP_400_BAD_REQUEST
    assert response_empty_answer.status_code == status.HTTP_400_BAD_REQUEST

    assert response_few_answers.json()["detail"] == "The number of answers must be equal to the number of questions"
    assert response_many_answers.json()["detail"] == "The number of answers must be equal to the number of questions"
    assert response_same_answers.json()["detail"] == "Error entering answers for a question 0"
    assert response_no_answer_2.json()["detail"] == "Error entering answers for a question 0 answer 1"
    assert response_bad_index.json()["detail"] == "Error entering answers for a question 0 answer 1"
    assert response_empty_answer.json()["detail"] == "Error entering answers for a question 0"




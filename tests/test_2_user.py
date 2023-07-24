from httpx import AsyncClient

import pytest
from fastapi import status

from utils.hashing import Hasher


async def test_create(ac: AsyncClient):
    response_create_1 = await ac.post("/user/", json={
        "username": "test1",
        "email": "test1@gmail.com",
        "password": "test1",
        "password_confirm": "test1",
    })

    response_create_2 = await ac.post("/user/", json={
        "username": "test2",
        "email": "test2@gmail.com",
        "password": "test2",
        "password_confirm": "test2",
    })

    response_create_3 = await ac.post("/user/", json={
        "username": "test3",
        "email": "test3@gmail.com",
        "password": "test3",
        "password_confirm": "test3",
    })

    response_create_4 = await ac.post("/user/", json={
        "username": "test4",
        "email": "test4@gmail.com",
        "password": "test4",
        "password_confirm": "test4",
    })

    response_create_5 = await ac.post("/user/", json={
        "username": "test5",
        "email": "test5@gmail.com",
        "password": "test5",
        "password_confirm": "test5",
    })

    assert response_create_1.status_code == status.HTTP_201_CREATED
    assert response_create_1.json()['email'] == "test1@gmail.com"
    assert response_create_2.status_code == status.HTTP_201_CREATED
    assert response_create_2.json()['email'] == "test2@gmail.com"
    assert response_create_3.status_code == status.HTTP_201_CREATED
    assert response_create_3.json()['email'] == "test3@gmail.com"
    assert response_create_4.status_code == status.HTTP_201_CREATED
    assert response_create_4.json()['email'] == "test4@gmail.com"
    assert response_create_5.status_code == status.HTTP_201_CREATED
    assert response_create_5.json()['email'] == "test5@gmail.com"


async def test_create_bad_password(ac: AsyncClient):
    response = await ac.post("/user/", json={
        "username": "bad_test",
        "email": "bad_test@gmail.com",
        "password": "test1",
        "password_confirm": "test2",
    })

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()['detail'][0]['msg'] == "Value error, passwords do not match"


async def test_create_bad_email(ac: AsyncClient):
    response = await ac.post("/user/", json={
        "username": "bad_email",
        "email": "test1@gmail.com",
        "password": "bad_email",
        "password_confirm": "bad_email",
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == " Key (email)=(test1@gmail.com) already exists."


async def test_login(ac: AsyncClient):
    response_login = await ac.post("/auth/login/", json={
        "email": "test1@gmail.com",
        "password": "test1",
    })

    assert response_login.status_code == status.HTTP_200_OK


async def test_login_bad(ac: AsyncClient):
    response_login = await ac.post("/auth/login/", json={
        "email": "no_such@gmail.com",
        "password": "no_such",
    })

    assert response_login.status_code == status.HTTP_400_BAD_REQUEST
    assert response_login.json()["detail"] == "Incorrect login or password"


async def test_me(ac: AsyncClient):
    response_login = await ac.post("/auth/login/", json={
        "email": "test1@gmail.com",
        "password": "test1",
    })

    access_token = response_login.json()['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}
    response_me = await ac.get("/auth/me/", headers=headers)

    assert response_login.status_code == status.HTTP_200_OK
    assert response_me.status_code == status.HTTP_200_OK
    assert response_me.json()['email'] == "test1@gmail.com"


async def test_me_bad(ac: AsyncClient):
    access_token = 'bad_token'
    headers = {"Authorization": f"Bearer {access_token}"}
    response_me = await ac.get("/auth/me/", headers=headers)

    assert response_me.status_code == status.HTTP_403_FORBIDDEN
    assert response_me.json()["detail"] == "Invalid token or expired token."


async def test_get(ac: AsyncClient, user_token: dict):
    response = await ac.get("/user/", headers=user_token)

    assert response.status_code == 200
    assert len(response.json()) == 5


async def test_get_id(ac: AsyncClient, user_token: dict):
    response = await ac.get("/user/3/", headers=user_token)

    assert response.status_code == 200
    assert response.json()["email"] == "test3@gmail.com"


async def test_get_bad_id(ac: AsyncClient, user_token: dict):
    response = await ac.get("/user/100/", headers=user_token)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_get_all(ac: AsyncClient, user_token: dict):
    response = await ac.get("/user/", headers=user_token)

    assert response.status_code == 200
    assert len(response.json()) == 5


@pytest.mark.parametrize("user_token", ('5'), indirect=True)
async def test_put(ac: AsyncClient, user_token: dict):
    response_put = await ac.put("/user/5/", json={
        "username": "new",
        "password": "test5",
        "password_confirm": "test5",
    }, headers=user_token)

    response_get = await ac.get("/user/5/", headers=user_token)

    assert response_put.status_code == status.HTTP_201_CREATED
    assert response_get.json()['username'] == 'new'
    assert Hasher.verify_password("test5", response_get.json()['hashed_password']) == True


async def test_put_bad_password(ac: AsyncClient, user_token: dict):
    response_put = await ac.put("/user/1/", json={
        "username": "username",
        "password": "12",
        "password_confirm": "qw",
    }, headers=user_token)

    assert response_put.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response_put.json()['detail'][0]['msg'] == "Value error, passwords do not match"


@pytest.mark.parametrize("user_token", ('3'), indirect=True)
async def test_put_bad_id(ac: AsyncClient, user_token: dict):
    response_put = await ac.put("/user/2/", json={
        "username": "username",
        "password": "qwer1234",
        "password_confirm": "qwer1234",
    }, headers=user_token)

    assert response_put.status_code == status.HTTP_400_BAD_REQUEST
    assert response_put.json()['detail'] == "This user cannot change the data"


@pytest.mark.parametrize('user_token', ('5'), indirect=True)
async def test_delete(ac: AsyncClient, user_token: dict):

    response = await ac.delete("/user/5/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["detail"] == "Success delete user"


async def test_delete_bad_id(ac: AsyncClient, user_token: dict):
    response = await ac.delete("/user/4/", headers=user_token)

    assert response.status_code == 400
    assert response.json()["detail"] == "This user cannot delete"

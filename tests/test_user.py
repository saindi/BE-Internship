from httpx import AsyncClient

from utils.hashing import Hasher


async def test_create(ac: AsyncClient):
    response_create = await ac.post("/user/", json={
        "username": "test_create",
        "email": "test_create@gmail.com",
        "password": "test_create_password",
        "password_confirm": "test_create_password",
    })

    assert response_create.status_code == 201
    assert response_create.json()['email'] == "test_create@gmail.com"


async def test_create_bad_password(ac: AsyncClient):
    response = await ac.post("/user/", json={
        "username": "bad_test",
        "email": "test_bad@gmail.com",
        "password": "test1",
        "password_confirm": "test2",
    })

    assert response.status_code == 422
    assert response.json()['detail'][0]['msg'] == "Value error, passwords do not match"


async def test_create_bad_email(ac: AsyncClient):
    response = await ac.post("/user/", json={
        "username": "bad_email",
        "email": "test_create@gmail.com",
        "password": "bad_email",
        "password_confirm": "bad_email",
    })

    assert response.status_code == 400
    assert response.json()['detail'] == " Key (email)=(test_create@gmail.com) already exists."


async def test_get(ac: AsyncClient):
    response_login = await ac.post("/auth/login", json={
        "email": "test_create@gmail.com",
        "password": "test_create_password",
    })

    access_token = response_login.json()['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}

    response = await ac.get("/user/3", headers=headers)

    assert response_login.status_code == 200
    assert response.status_code == 200
    assert response.json()["email"] == "test_create@gmail.com"


async def test_get_all(ac: AsyncClient):
    response_login = await ac.post("/auth/login", json={
        "email": "test_create@gmail.com",
        "password": "test_create_password",
    })

    access_token = response_login.json()['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}

    response = await ac.get("/user/", headers=headers)

    assert response_login.status_code == 200
    assert response.status_code == 200
    assert len(response.json()) == 3


async def test_put(ac: AsyncClient):
    response_login = await ac.post("/auth/login", json={
        "email": "test_create@gmail.com",
        "password": "test_create_password",
    })

    access_token = response_login.json()['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}

    response_put = await ac.put("/user/2", json={
        "email": "new@gmail.com",
        "password": "new",
        "password_confirm": "new",
    }, headers=headers)

    response_get = await ac.get("/user/2")

    assert response_put.status_code == 201
    assert Hasher.verify_password("new", response_get.json()['hashed_password']) == True


async def test_put(ac: AsyncClient):
    response_login = await ac.post("/auth/login", json={
        "email": "test_create@gmail.com",
        "password": "test_create_password",
    })

    access_token = response_login.json()['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}

    response_put = await ac.put("/user/3", json={
        "username": "username",
        "password": "new",
        "password_confirm": "new",
    }, headers=headers)

    response_get = await ac.get("/user/3", headers=headers)

    assert response_put.status_code == 201
    assert response_get.json()['username'] == 'username'
    assert Hasher.verify_password("new", response_get.json()['hashed_password']) == True


async def test_put_bad(ac: AsyncClient):
    response_login = await ac.post("/auth/login", json={
        "email": "test_create@gmail.com",
        "password": "new",
    })

    access_token = response_login.json()['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}

    response_put = await ac.put("/user/2", json={
        "username": "username",
        "password": "new1",
        "password_confirm": "new1",
    }, headers=headers)

    assert response_put.status_code == 400
    assert response_put.json()["detail"] == "This user cannot change the data"


async def test_delete(ac: AsyncClient):
    response_login = await ac.post("/auth/login", json={
        "email": "test_create@gmail.com",
        "password": "new",
    })

    access_token = response_login.json()['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}

    response = await ac.delete("/user/3", headers=headers)

    assert response_login.status_code == 200
    assert response.status_code == 200
    assert response.json()["detail"] == "Success delete user"


async def test_delete_bad(ac: AsyncClient):
    response_login = await ac.post("/auth/login", json={
        "email": "test_token@gmail.com",
        "password": "test_token_password",
    })

    access_token = response_login.json()['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}

    response = await ac.delete("/user/2", headers=headers)

    assert response_login.status_code == 200
    assert response.status_code == 400
    assert response.json()["detail"] == "This user cannot delete"

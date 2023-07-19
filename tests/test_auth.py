from httpx import AsyncClient


async def test_login(ac: AsyncClient):
    response_create = await ac.post("/user/", json={
        "username": "test_token",
        "email": "test_token@gmail.com",
        "password": "test_token_password",
        "password_confirm": "test_token_password",
    })

    response_login = await ac.post("/auth/login", json={
        "email": "test_token@gmail.com",
        "password": "test_token_password",
    })

    assert response_create.status_code == 201
    assert response_login.status_code == 200


async def test_login_bad(ac: AsyncClient):
    response_login = await ac.post("/auth/login", json={
        "email": "no_such@gmail.com",
        "password": "no_such",
    })

    assert response_login.status_code == 400
    assert response_login.json()["detail"] == "Incorrect login or password"


async def test_me(ac: AsyncClient):
    response_login = await ac.post("/auth/login", json={
        "email": "test_token@gmail.com",
        "password": "test_token_password",
    })

    access_token = response_login.json()['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}
    response_me = await ac.get("/auth/me", headers=headers)

    assert response_login.status_code == 200
    assert response_me.status_code == 200
    assert response_me.json()['email'] == "test_token@gmail.com"


async def test_me_bad(ac: AsyncClient):
    access_token = 'bad_token'
    headers = {"Authorization": f"Bearer {access_token}"}
    response_me = await ac.get("/auth/me", headers=headers)

    assert response_me.status_code == 403
    assert response_me.json()["detail"] == "Invalid token or expired token."
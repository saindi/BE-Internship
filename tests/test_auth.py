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


async def test_auth0(ac: AsyncClient):
    auth0_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjFCZVVEb2MySE80dXNXU056TEV6YSJ9.eyJlbWFpbCI6IjEyMzQ0QGdtYWlsLmNvbSIsImlzcyI6Imh0dHBzOi8vZGV2LWdpbnQxanhxbnNnenZ2OHcudXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDY0YjgxMWM0NDVmNTkzODRmNjU5NzMxYyIsImF1ZCI6WyJodHRwczovL3Rlc3QtaW50ZXJuc2hpcC1leGFtcGxlLmNvbSIsImh0dHBzOi8vZGV2LWdpbnQxanhxbnNnenZ2OHcudXMuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTY4OTc4NDc3NCwiZXhwIjoxNjg5ODcxMTc0LCJhenAiOiJZUGRKRUFYb3dBV29BdVRsUk0zZ2V3NDNhbjU2Z0I4YSIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwifQ.A-SzlXU2KmS47-FjPVfNQO3k8Gdkol97s6SKArJpBa_o3uwlFz2eLIWxZTngQTQutHCq7HmLQh_BYO7ZCP_TsEjtjf_-ekOxWIuZ4IqAaqzdu-EWyv_mK-P3xNd6bnONbi4L9zrMNVKRB_kj0-jKFwEF_mFCBsn5k5ui9pDmH2MQfDTSIn66F_WSWH2hDUUwCzc7uulGgkTgWzhS9jlQciQT92mT0BKpbXXwmNUek8OXHjG42SyLoNIzFqCKKD5Ro_354ORYKEM6M4tyGbWiVv9az-Xn-oNQEILkOFSWFzw_CPp-4oS5Kub6YabIpMAoPPSqRh5CDZ30htqiYUUaJQ'

    headers = {"Authorization": f"Bearer {auth0_token}"}

    response_me = await ac.get("/auth/me", headers=headers)

    assert response_me.status_code == 200
    assert response_me.json()['email'] == '12344@gmail.com'
from httpx import AsyncClient

from utils.hashing import Hasher


async def test_post(ac: AsyncClient):
    response = await ac.post("/user/", json={
        "email": "test1@gmail.com",
        "password": "test",
    })

    assert response.status_code == 201


async def test_get(ac: AsyncClient):
    response = await ac.get("/user/1")

    assert response.status_code == 200
    assert response.json()["email"] == "test1@gmail.com"


async def test_get_all(ac: AsyncClient):
    response_post = await ac.post("/user/", json={
        "email": "test2@gmail.com",
        "password": "test",
    })

    response_get = await ac.get("/user/")

    assert response_post.status_code == 201
    assert response_get.status_code == 200
    assert len(response_get.json()) == 2


async def test_put(ac: AsyncClient):
    response_put = await ac.put("/user/2", json={
        "email": "new@gmail.com",
        "password": "new",
    })

    response_get = await ac.get("/user/2")

    assert response_put.status_code == 201
    assert Hasher.verify_password("new", response_get.json()['hashed_password']) == True


async def test_delete(ac: AsyncClient):
    response_delete_1 = await ac.delete("/user/1")
    response_get_1 = await ac.get("/user/")

    assert response_delete_1.status_code == 200
    assert response_get_1.status_code == 200
    assert len(response_get_1.json()) == 1

    response_delete_2 = await ac.delete("/user/2")
    response_get_2 = await ac.get("/user/")

    assert response_delete_2.status_code == 200
    assert response_get_2.status_code == 200
    assert len(response_get_2.json()) == 0

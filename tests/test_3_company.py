from httpx import AsyncClient

from fastapi import status


async def get_headers(ac: AsyncClient, user_id: int = 1) -> dict:
    response_login = await ac.post("/auth/login/", json={
        "email": f"test{user_id}@gmail.com",
        "password": f"test{user_id}",
    })

    access_token = response_login.json()['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}

    return headers


async def test_create(ac: AsyncClient):
    headers = await get_headers(ac)

    response_1 = await ac.post("/company/", json={
        "name": "company1",
        "description": "company1"
    }, headers=headers)

    response_2 = await ac.post("/company/", json={
        "name": "company2",
        "description": "company2"
    }, headers=headers)

    headers = await get_headers(ac, 2)

    response_3 = await ac.post("/company/", json={
        "name": "company3",
        "description": "company3"
    }, headers=headers)

    assert response_1.status_code == status.HTTP_201_CREATED
    assert response_1.json()['name'] == "company1"
    assert response_2.status_code == status.HTTP_201_CREATED
    assert response_2.json()['name'] == "company2"
    assert response_3.status_code == status.HTTP_201_CREATED
    assert response_3.json()['name'] == "company3"


async def test_create_bad(ac: AsyncClient):
    headers = await get_headers(ac)

    response = await ac.post("/company/", json={
        "name": "company1",
        "description": "company1"
    }, headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == " Key (name)=(company1) already exists."


async def test_get_all(ac: AsyncClient):
    headers = await get_headers(ac)

    response = await ac.get("/company/", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 3


async def test_get_by_id(ac: AsyncClient):
    headers = await get_headers(ac)

    response_create = await ac.get("/company/1/", headers=headers)

    assert response_create.status_code == status.HTTP_200_OK
    assert response_create.json()['name'] == 'company1'


async def test_get_by_id_bad(ac: AsyncClient):
    headers = await get_headers(ac)

    response_create = await ac.get("/company/100/", headers=headers)

    assert response_create.status_code == status.HTTP_400_BAD_REQUEST
    assert response_create.json()['detail'] == "No such company with id 100"


async def test_put(ac: AsyncClient):
    headers = await get_headers(ac)

    response = await ac.put("/company/1/", json={
        "name": "new",
        "description": "new",
        "is_hidden": True
    }, headers=headers)

    assert response.status_code == 201
    assert response.json()['name'] == 'new'
    assert response.json()['description'] == 'new'


async def test_put_bad_user(ac: AsyncClient):
    headers = await get_headers(ac, 2)

    response = await ac.put("/company/2/", json={
        "name": "1",
        "description": "new",
        "is_hidden": True
    }, headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == 'This user cannot change the company'


async def test_put_bad_name(ac: AsyncClient):
    headers = await get_headers(ac)

    response = await ac.put("/company/1/", json={
        "name": "company2",
        "description": "new",
        "is_hidden": True
    }, headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == " Key (name)=(company2) already exists."


async def test_delete(ac: AsyncClient):
    headers = await get_headers(ac)

    response = await ac.delete("/company/2/", headers=headers)

    assert response.status_code == 200
    assert response.json()['detail'] == "Success delete company"


async def test_delete_bad_id(ac: AsyncClient):
    headers = await get_headers(ac)

    response = await ac.delete("/company/100/", headers=headers)

    assert response.status_code == 400
    assert response.json()["detail"] == "No such company with id 100"


async def test_delete_bad_user(ac: AsyncClient):
    headers = await get_headers(ac, 2)

    response = await ac.delete("/company/1/", headers=headers)

    assert response.status_code == 400
    assert response.json()["detail"] == "This user cannot delete сompany"

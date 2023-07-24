from httpx import AsyncClient

import pytest
from fastapi import status


async def test_create(ac: AsyncClient, user_token: dict):
    response_1 = await ac.post("/company/", json={
        "name": "company1",
        "description": "company1"
    }, headers=user_token)

    response_2 = await ac.post("/company/", json={
        "name": "company2",
        "description": "company2"
    }, headers=user_token)

    response_3 = await ac.post("/company/", json={
        "name": "company3",
        "description": "company3"
    }, headers=user_token)

    assert response_1.status_code == status.HTTP_201_CREATED
    assert response_1.json()['name'] == "company1"
    assert response_2.status_code == status.HTTP_201_CREATED
    assert response_2.json()['name'] == "company2"
    assert response_3.status_code == status.HTTP_201_CREATED
    assert response_3.json()['name'] == "company3"


async def test_create_bad(ac: AsyncClient, user_token: dict):

    response = await ac.post("/company/", json={
        "name": "company1",
        "description": "company1"
    }, headers=user_token)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == " Key (name)=(company1) already exists."


async def test_get_all(ac: AsyncClient, user_token: dict):
    response = await ac.get("/company/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 3


async def test_get_by_id(ac: AsyncClient, user_token: dict):
    response_create = await ac.get("/company/1/", headers=user_token)

    assert response_create.status_code == status.HTTP_200_OK
    assert response_create.json()['name'] == 'company1'


async def test_get_by_id_bad(ac: AsyncClient, user_token: dict):
    response_create = await ac.get("/company/100/", headers=user_token)

    assert response_create.status_code == status.HTTP_400_BAD_REQUEST
    assert response_create.json()['detail'] == "No such company with id 100"


async def test_put(ac: AsyncClient, user_token: dict):
    response = await ac.put("/company/1/", json={
        "name": "new",
        "description": "new",
        "is_hidden": True
    }, headers=user_token)

    assert response.status_code == 201
    assert response.json()['name'] == 'new'
    assert response.json()['description'] == 'new'


@pytest.mark.parametrize("user_token", ('2'), indirect=True)
async def test_put_bad_user(ac: AsyncClient, user_token: dict):

    response = await ac.put("/company/2/", json={
        "name": "1",
        "description": "new",
        "is_hidden": True
    }, headers=user_token)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == 'This user cannot change the company'


async def test_put_bad_name(ac: AsyncClient, user_token: dict):
    response = await ac.put("/company/1/", json={
        "name": "company2",
        "description": "new",
        "is_hidden": True
    }, headers=user_token)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == " Key (name)=(company2) already exists."


async def test_delete(ac: AsyncClient, user_token: dict):
    response = await ac.delete("/company/2/", headers=user_token)

    assert response.status_code == 200
    assert response.json()['detail'] == "Success delete company"


async def test_delete_bad_id(ac: AsyncClient, user_token: dict):
    response = await ac.delete("/company/100/", headers=user_token)

    assert response.status_code == 400
    assert response.json()["detail"] == "No such company with id 100"


@pytest.mark.parametrize("user_token", ('2'), indirect=True)
async def test_delete_bad_user(ac: AsyncClient, user_token: dict):
    response = await ac.delete("/company/1/", headers=user_token)

    assert response.status_code == 400
    assert response.json()["detail"] == "This user cannot delete сompany"

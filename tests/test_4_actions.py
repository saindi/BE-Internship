from httpx import AsyncClient

import pytest
from fastapi import status


@pytest.mark.parametrize('user_token', ('3'), indirect=True)
async def test_request(ac: AsyncClient, user_token: dict):
    response_1 = await ac.post("/user/request/", params={
        "company_id": 1,
    }, headers=user_token)

    response_2 = await ac.post("/user/request/", params={
        "company_id": 3,
    }, headers=user_token)

    assert response_1.json()['id_company'] == 1
    assert response_1.status_code == status.HTTP_201_CREATED
    assert response_2.json()['id_company'] == 3
    assert response_2.status_code == status.HTTP_201_CREATED


@pytest.mark.parametrize('user_token', ('3'), indirect=True)
async def test_requests_user(ac: AsyncClient, user_token: dict):

    response_1 = await ac.get("/user/requests/", headers=user_token)

    assert len(response_1.json()) == 2


@pytest.mark.parametrize('user_token', ('3'), indirect=True)
async def test_request_bad_id(ac: AsyncClient, user_token: dict):
    response_1 = await ac.post("/user/request/", params={
        "company_id": 100,
    }, headers=user_token)

    assert response_1.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize('user_token', ('3'), indirect=True)
async def test_request_already(ac: AsyncClient, user_token: dict):
    response_1 = await ac.post("/user/request/", params={
        "company_id": 1,
    }, headers=user_token)

    assert response_1.status_code == status.HTTP_400_BAD_REQUEST
    assert response_1.json()['detail'] == 'You already have such a request'


@pytest.mark.parametrize('user_token', ('3'), indirect=True)
async def test_request_delete(ac: AsyncClient, user_token: dict):
    response = await ac.delete("/user/request/2/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize('user_token', ('3'), indirect=True)
async def test_request_delete_bad(ac: AsyncClient, user_token: dict):
    response = await ac.delete("/user/request/2/", headers=user_token)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_request_accept(ac: AsyncClient, user_token: dict):
    response = await ac.get("/company/3/request/1/accept/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK


async def test_invite(ac: AsyncClient, user_token: dict):
    response_1 = await ac.post("/company/1/invitation/", params={'user_id': 2}, headers=user_token)
    response_2 = await ac.post("/company/1/invitation/", params={'user_id': 4}, headers=user_token)

    assert response_1.status_code == status.HTTP_201_CREATED
    assert response_2.status_code == status.HTTP_201_CREATED


@pytest.mark.parametrize('user_token', ('2'), indirect=True)
async def test_invite_accept(ac: AsyncClient, user_token: dict):
    response = await ac.get("/user/invitation/1/accept/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize('user_token', ('4'), indirect=True)
async def test_invite_reject(ac: AsyncClient,  user_token: dict):
    response = await ac.get("/user/invitation/2/reject/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK


async def test_add_admin(ac: AsyncClient, user_token: dict):
    response = await ac.get("/company/1/admin/2/set/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK


async def test_admins(ac: AsyncClient, user_token: dict):
    response = await ac.get("/company/1/admins/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


async def test_remove_admin(ac: AsyncClient, user_token: dict):
    response_1 = await ac.get("/company/1/admin/2/remove/", headers=user_token)
    response_2 = await ac.get("/company/1/admins/", headers=user_token)

    assert response_1.status_code == status.HTTP_200_OK
    assert response_2.status_code == status.HTTP_200_OK
    assert len(response_2.json()) == 0

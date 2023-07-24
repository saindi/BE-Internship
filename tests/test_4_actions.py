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


async def test_request(ac: AsyncClient):
    headers = await get_headers(ac, 3)

    response_1 = await ac.post("/user/request/", params={
        "company_id": 1,
    }, headers=headers)

    response_2 = await ac.post("/user/request/", params={
        "company_id": 3,
    }, headers=headers)

    assert response_1.json()['id_company'] == 1
    assert response_1.status_code == status.HTTP_200_OK
    assert response_2.json()['id_company'] == 3
    assert response_2.status_code == status.HTTP_200_OK


async def test_requests_user(ac: AsyncClient):
    headers = await get_headers(ac, 3)

    response_1 = await ac.get("/user/requests/", headers=headers)

    assert len(response_1.json()) == 2


async def test_request_bad_id(ac: AsyncClient):
    headers = await get_headers(ac, 3)

    response_1 = await ac.post("/user/request/", params={
        "company_id": 100,
    }, headers=headers)

    assert response_1.status_code == status.HTTP_400_BAD_REQUEST


async def test_request_already(ac: AsyncClient):
    headers = await get_headers(ac, 3)

    response_1 = await ac.post("/user/request/", params={
        "company_id": 1,
    }, headers=headers)

    assert response_1.status_code == status.HTTP_400_BAD_REQUEST
    assert response_1.json()['detail'] == 'You already have such a request'


async def test_request_delete(ac: AsyncClient):
    headers = await get_headers(ac, 3)

    response = await ac.delete("/user/request/2/", headers=headers)

    assert response.status_code == status.HTTP_200_OK


async def test_request_delete_bad(ac: AsyncClient):
    headers = await get_headers(ac, 3)

    response = await ac.delete("/user/request/2/", headers=headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


async def test_request_accept(ac: AsyncClient):
    headers = await get_headers(ac, 2)

    response = await ac.get("/company/3/request/1/accept/", headers=headers)

    assert response.status_code == status.HTTP_200_OK


async def test_invite(ac: AsyncClient):
    headers = await get_headers(ac)

    response_1 = await ac.post("/company/1/invitation/", params={'user_id': 2}, headers=headers)
    response_2 = await ac.post("/company/1/invitation/", params={'user_id': 4}, headers=headers)

    assert response_1.status_code == status.HTTP_200_OK
    assert response_2.status_code == status.HTTP_200_OK


async def test_invite_accept(ac: AsyncClient):
    headers = await get_headers(ac, 2)

    response = await ac.get("/user/invitation/1/accept/", headers=headers)

    assert response.status_code == status.HTTP_200_OK


async def test_invite_reject(ac: AsyncClient):
    headers = await get_headers(ac, 4)

    response = await ac.get("/user/invitation/2/reject/", headers=headers)

    assert response.status_code == status.HTTP_200_OK


async def test_add_admin(ac: AsyncClient):
    headers = await get_headers(ac)

    response = await ac.get("/company/1/admin/2/set/", headers=headers)

    assert response.status_code == status.HTTP_200_OK


async def test_admins(ac: AsyncClient):
    headers = await get_headers(ac)

    response = await ac.get("/company/1/admins/", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


async def test_remove_admin(ac: AsyncClient):
    headers = await get_headers(ac)

    response_1 = await ac.get("/company/1/admin/2/remove/", headers=headers)
    response_2 = await ac.get("/company/1/admins/", headers=headers)

    assert response_1.status_code == status.HTTP_200_OK
    assert response_2.status_code == status.HTTP_200_OK
    assert len(response_2.json()) == 0

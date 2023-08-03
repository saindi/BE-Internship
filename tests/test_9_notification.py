import pytest
from httpx import AsyncClient

from fastapi import status


async def test_user_1_notifications(ac: AsyncClient, user_token: dict):
    response = await ac.get("/user/1/notifications/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 3


@pytest.mark.parametrize('user_token', ('2'), indirect=True)
async def test_user_2_notifications(ac: AsyncClient, user_token: dict):
    response = await ac.get("/user/2/notifications/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2


@pytest.mark.parametrize('user_token', ('3'), indirect=True)
async def test_user_3_notifications(ac: AsyncClient, user_token: dict):
    response = await ac.get("/user/3/notifications/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2


async def test_mark_read(ac: AsyncClient, user_token: dict):
    response = await ac.put("/user/1/notification/1/mark_read/", headers=user_token)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['status'] == 'READ'


async def test_mark_read_bad_id(ac: AsyncClient, user_token: dict):
    response = await ac.put("/user/1/notification/100/mark_read/", headers=user_token)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == 'Notification not found'


async def test_delete_read(ac: AsyncClient, user_token: dict):
    response_delete = await ac.delete("/user/1/notifications/delete_read/", headers=user_token)
    response_all = await ac.get("/user/1/notifications/", headers=user_token)

    assert response_delete.status_code == status.HTTP_200_OK
    assert response_delete.json()['detail'] == 'Success delete notifications'
    assert response_all.status_code == status.HTTP_200_OK
    assert len(response_all.json()) == 2


async def test_delete_read_no_read_notific(ac: AsyncClient, user_token: dict):
    response_delete = await ac.delete("/user/1/notifications/delete_read/", headers=user_token)

    assert response_delete.status_code == status.HTTP_200_OK
    assert response_delete.json()['detail'] == 'No such read notifications'

from httpx import AsyncClient

auth0_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjFCZVVEb2MySE80dXNXU056TEV6YSJ9.eyJlbWFpbCI6IjEyMzQ0QGdtYWlsLmNvbSIsImlzcyI6Imh0dHBzOi8vZGV2LWdpbnQxanhxbnNnenZ2OHcudXMuYXV0aDAuY29tLyIsInN1YiI6ImF1dGgwfDY0YjgxMWM0NDVmNTkzODRmNjU5NzMxYyIsImF1ZCI6WyJodHRwczovL3Rlc3QtaW50ZXJuc2hpcC1leGFtcGxlLmNvbSIsImh0dHBzOi8vZGV2LWdpbnQxanhxbnNnenZ2OHcudXMuYXV0aDAuY29tL3VzZXJpbmZvIl0sImlhdCI6MTY4OTc4NDc3NCwiZXhwIjoxNjg5ODcxMTc0LCJhenAiOiJZUGRKRUFYb3dBV29BdVRsUk0zZ2V3NDNhbjU2Z0I4YSIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgZW1haWwifQ.A-SzlXU2KmS47-FjPVfNQO3k8Gdkol97s6SKArJpBa_o3uwlFz2eLIWxZTngQTQutHCq7HmLQh_BYO7ZCP_TsEjtjf_-ekOxWIuZ4IqAaqzdu-EWyv_mK-P3xNd6bnONbi4L9zrMNVKRB_kj0-jKFwEF_mFCBsn5k5ui9pDmH2MQfDTSIn66F_WSWH2hDUUwCzc7uulGgkTgWzhS9jlQciQT92mT0BKpbXXwmNUek8OXHjG42SyLoNIzFqCKKD5Ro_354ORYKEM6M4tyGbWiVv9az-Xn-oNQEILkOFSWFzw_CPp-4oS5Kub6YabIpMAoPPSqRh5CDZ30htqiYUUaJQ'
headers = {"Authorization": f"Bearer {auth0_token}"}


async def test_create(ac: AsyncClient):
    response = await ac.post("/company/", json={
        "name": "test_company",
        "description": "test_company_description"
    }, headers=headers)

    assert response.status_code == 201
    assert response.json()['name'] == "test_company"


async def test_create_bad(ac: AsyncClient):
    response = await ac.post("/company/", json={
        "name": "test_company",
        "description": "test_company_description"
    }, headers=headers)

    assert response.status_code == 400
    assert response.json()["detail"] == " Key (name)=(test_company) already exists."


async def test_get_all(ac: AsyncClient):
    response = await ac.get("/company/", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_get_by_id(ac: AsyncClient):
    response_create = await ac.get("/company/1", headers=headers)

    assert response_create.status_code == 200
    assert response_create.json()['name'] == 'test_company'
    assert response_create.json()['owner']['email'] == '12344@gmail.com'


async def test_put(ac: AsyncClient):
    response = await ac.put("/company/1", json={
        "name": "string_new",
        "description": "string_new",
        "is_hidden": False
    }, headers=headers)

    assert response.status_code == 201
    assert response.json()['name'] == 'string_new'
    assert response.json()['description'] == 'string_new'


async def test_delete(ac: AsyncClient):
    response = await ac.delete("/company/1", headers=headers)

    assert response.status_code == 200
    assert response.json()['detail'] == 'Success delete сompany'


async def test_delete_bad(ac: AsyncClient):
    response = await ac.delete("/company/2", headers=headers)

    assert response.status_code == 400
    assert response.json()["detail"] == "No such сompany with id 2"

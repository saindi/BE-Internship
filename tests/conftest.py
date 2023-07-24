import asyncio
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from auth.auth import JWTBearer, jwt_bearer
from db.database import get_async_session, metadata
from config import global_settings
from main import app
from user.models import User
from utils.hashing import Hasher

engine_test = create_async_engine(global_settings.postgresql_test_url, poolclass=NullPool)
async_session_maker = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
metadata.bind = engine_test


class OverrideJWTBearer(JWTBearer):
    async def verify_jwt(self, token: str):
        payload = self.decode_jwt(token)

        if not payload:
            return None

        async with async_session_maker() as db:
            user = await User.get_by_fields(db, email=payload['email'])

        if not user:
            return None

        return user

    async def verify_auth0(self, token: str):
        payload = self.decode_auth0(token)

        if not payload:
            return None

        async with async_session_maker() as db:
            user = await User.get_by_fields(db, email=payload['email'])

            if user:
                return user

            new_user = User(
                email=payload['email'],
                username=payload['email'],
                hashed_password=Hasher.get_password_hash(payload['email'])
            )

            await new_user.create(db)

        return new_user


override_jwt_bearer = OverrideJWTBearer()


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

app.dependency_overrides[get_async_session] = override_get_async_session
app.dependency_overrides[jwt_bearer] = override_jwt_bearer


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.drop_all)


@pytest.fixture(scope='session')
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


client = TestClient(app)


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def user_token(request, ac: AsyncClient) -> dict:
    user_id = int(request.param) if hasattr(request, 'param') else 1

    response_login = await ac.post("/auth/login/", json={
        "email": f"test{user_id}@gmail.com",
        "password": f"test{user_id}",
    })

    access_token = response_login.json()['access_token']
    headers = {"Authorization": f"Bearer {access_token}"}

    yield headers

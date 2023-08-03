from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from config import global_settings

engine = create_async_engine(
    global_settings.postgresql_url,
    echo=False,
    future=True
)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, future=True)

metadata = MetaData()


class Base(DeclarativeBase):
    metadata = metadata


async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session


def get_sync_session():
    engine_sync = create_engine(global_settings.postgresql_sync_url, echo=False)
    session_sync = sessionmaker(bind=engine_sync)

    return session_sync()

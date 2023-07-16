from typing import Type, List, TypeVar, Dict
from datetime import datetime
import re

from fastapi import status, HTTPException
from sqlalchemy import select
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from db.database import Base
from utils.hashing import Hasher

TBase = TypeVar("TBase", bound="BaseModel")


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @classmethod
    async def get_all(cls: Type[TBase], db: AsyncSession, skip: int = 0, limit: int = 100) -> List[TBase]:
        query = select(cls).offset(skip).limit(limit)
        result = await db.execute(query)
        instances = result.scalars().all()

        return instances

    @classmethod
    async def get_by_id(cls: Type[TBase], db: AsyncSession, obj_id: int) -> TBase:
        query = select(cls).where(cls.id == obj_id)
        result = await db.execute(query)
        instance = result.scalars().first()

        if not instance:
            detail = f"No such {cls.__tablename__} with id {obj_id}"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

        return instance

    async def create(self, db: AsyncSession) -> TBase:
        try:
            db.add(self)
            await db.commit()
            await db.refresh(self)

            return self

        except IntegrityError as e:
            detail = re.search(r'DETAIL: (.*)', e.orig.args[0])[1]
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    @classmethod
    async def update(cls: Type[TBase], db: AsyncSession, obj_id: int, data) -> TBase:
        instance = await cls.get_by_id(db, obj_id)

        instance.email = data.email
        instance.hashed_password = Hasher.get_password_hash(data.password)

        await db.commit()
        await db.refresh(instance)

        return instance

    @classmethod
    async def delete(cls: Type[TBase], db: AsyncSession, obj_id: int) -> Dict:
        instance = await cls.get_by_id(db, obj_id)

        await db.delete(instance)
        await db.commit()

        return {'detail': f'Success delete {cls.__tablename__}'}

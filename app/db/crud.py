from typing import Type, List, TypeVar, Dict
import re

from fastapi import status, HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from db.database import Base

TBase = TypeVar("TBase", bound="BaseModel")


class BaseCRUD(Base):
    __abstract__ = True

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

    @classmethod
    async def get_by_fields(
            cls: Type[TBase],
            db: AsyncSession,
            return_single: bool = True,
            skip: int = None,
            limit: int = None,
            **kwargs
    ) -> List[TBase]:
        filters = [getattr(cls, field) == value for field, value in kwargs.items()]
        query = select(cls).where(and_(*filters)).offset(skip).limit(limit)
        result = await db.execute(query)
        instances = result.scalars().all()

        if not instances:
            return None

        return instances[0] if return_single else instances

    async def create(self, db: AsyncSession) -> TBase:
        try:
            db.add(self)
            await db.commit()
            await db.refresh(self)

        except IntegrityError as e:
            detail = re.search(r'DETAIL: (.*)', e.orig.args[0])[1]
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    async def update(self, db: AsyncSession, data) -> TBase:
        for key, value in dict(data).items():
            setattr(self, key, value)

        try:
            await db.commit()
            await db.refresh(self)

        except IntegrityError as e:
            detail = re.search(r'DETAIL: (.*)', e.orig.args[0])[1]
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    async def delete(self, db: AsyncSession) -> Dict:
        await db.delete(self)
        await db.commit()

        return {'detail': f'Success delete {self.__tablename__}'}

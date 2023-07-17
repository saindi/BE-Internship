from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_async_session
from user.schemas import UserSchema, SignUpRequest, UserUpdateRequest
from user.models import UserModel
from utils.hashing import Hasher

router = APIRouter(prefix='/user')


@router.get("/", response_model=List[UserSchema])
async def get_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_async_session)):
    users = await UserModel.get_all(db, skip, limit)

    return users


@router.get("/{user_id}", response_model=UserSchema)
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_async_session)):
    users = await UserModel.get_by_id(db, user_id)

    return users


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(request: SignUpRequest, db: AsyncSession = Depends(get_async_session)):
    new_user = UserModel(email=request.email, hashed_password=Hasher.get_password_hash(request.password))

    user = await new_user.create(db)

    return user


@router.put("/{user_id}", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def update_user(user_id: int, data: UserUpdateRequest, db: AsyncSession = Depends(get_async_session)):
    users = await UserModel.update(db, user_id, data)

    return users


@router.delete("/{user_id}")
async def delete_user(user_id: int,  db: AsyncSession = Depends(get_async_session)):
    return await UserModel.delete(db, user_id)

from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.database import get_async_session
from schemas.user import UserSchema, SignUpRequest, UserUpdateRequest
from models.user import UserModel
from utils.hashing import Hasher

router = APIRouter(prefix='/user')


@router.get("/", response_model=List[UserSchema])
async def get_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_async_session)):
    query = select(UserModel).offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()

    return users


@router.get("/{user_id}", response_model=UserSchema)
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_async_session)):
    result = await db.get(UserModel, user_id)

    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such user")

    return result


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(request: SignUpRequest, db: AsyncSession = Depends(get_async_session)):
    existing_user = await db.execute(select(UserModel).filter_by(email=request.email))

    if existing_user.fetchone():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")

    new_user = UserModel(email=request.email, hashed_password=Hasher.get_password_hash(request.password))

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.put("/{user_id}", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def update_user(user_id: int, data: UserUpdateRequest, db: AsyncSession = Depends(get_async_session)):
    result = await db.get(UserModel, user_id)

    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such user")

    result.email = data.email
    result.hashed_password = Hasher.get_password_hash(data.password)

    await db.commit()
    await db.refresh(result)

    return result


@router.delete("/{user_id}")
async def delete_user(user_id: int,  db: AsyncSession = Depends(get_async_session)):
    result = await db.get(UserModel, user_id)

    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such user")

    await db.delete(result)
    await db.commit()

    return {'detail': 'Success delete data'}

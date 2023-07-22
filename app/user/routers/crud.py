from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import jwt_bearer
from company.models import RoleModel, RoleEnum
from db.database import get_async_session
from user.schemas import UserSchema, UserCreateRequest, UserUpdateRequest, UserNewData
from user.models import UserModel
from utils.hashing import Hasher

router = APIRouter(prefix='/user')


@router.get("/", response_model=List[UserSchema], dependencies=[Depends(jwt_bearer)])
async def get_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_async_session)):
    users = await UserModel.get_all(db, skip, limit)

    return users


@router.get("/{user_id}", response_model=UserSchema, dependencies=[Depends(jwt_bearer)])
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_async_session)):
    users = await UserModel.get_by_id(db, user_id)

    return users


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(request: UserCreateRequest, db: AsyncSession = Depends(get_async_session)):
    new_user = UserModel(
        email=request.email,
        username=request.username,
        hashed_password=Hasher.get_password_hash(request.password)
    )

    await new_user.create(db)

    return new_user


@router.put("/{user_id}", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def update_user(
        user_id: int,
        data: UserUpdateRequest,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    affected_user = await UserModel.get_by_id(db, user_id)

    if not user.can_edit(affected_user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='This user cannot change the data')

    await affected_user.update(db, UserNewData(data))

    return user


@router.delete("/{user_id}")
async def delete_user(
        user_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    affected_user = await UserModel.get_by_id(db, user_id)

    roles = await RoleModel.get_by_fields(db, False, id_user=affected_user.id, role=RoleEnum.OWNER)

    if roles:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='First, delete the companies where you are the creator.')

    if not user.can_delete(affected_user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='This user cannot delete')

    return await affected_user.delete(db)

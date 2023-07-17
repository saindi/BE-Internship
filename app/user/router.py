from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_async_session
from user.auth import sign_jwt, decode_jwt
from user.schemas import UserSchema, SignUpRequest, SignInRequest, UserUpdateRequest, TokenSchema
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


@router.post("/signup", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(request: SignUpRequest, db: AsyncSession = Depends(get_async_session)):
    new_user = UserModel(email=request.email, hashed_password=Hasher.get_password_hash(request.password))

    user = await new_user.create(db)

    return user


@router.put("/{user_id}", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def update_user(user_id: int, data: UserUpdateRequest, db: AsyncSession = Depends(get_async_session)):
    new_data = {
        'email': data.email,
        'hashed_password': Hasher.get_password_hash(data.password)
    }

    users = await UserModel.update(db, user_id, new_data)

    return users


@router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_async_session)):
    return await UserModel.delete(db, user_id)


@router.post("/signin", response_model=TokenSchema)
async def signin(request: SignInRequest, db: AsyncSession = Depends(get_async_session)):
    user = await UserModel.get_by_fields(db, email=request.email)

    if not user or user.user_verification(request.password) == False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect login or password ')

    return sign_jwt(user.email, request.password)


@router.post("/me", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def me(token: TokenSchema, db: AsyncSession = Depends(get_async_session)):
    data = decode_jwt(token.access_token)

    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect token')

    user = await UserModel.get_by_fields(db, email=data['email'])

    if not user or user.user_verification(data['password']) == False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect token')

    return user

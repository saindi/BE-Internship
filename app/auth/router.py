from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_async_session
from auth.auth import jwt_bearer, JWTBearer
from auth.schemas import LoginSchema, AccessTokenSchema, RefreshTokenSchema
from user.models.models import UserModel
from user.schemas import UserSchema, UserWithToken

router = APIRouter(prefix='/auth')


@router.post("/login/", response_model=UserWithToken)
async def login(request: LoginSchema, db: AsyncSession = Depends(get_async_session)):
    user = await UserModel.get_by_fields(db, email=request.email)

    if not user or user.user_verification(request.password) == False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect login or password')

    tokes = jwt_bearer.sign_jwt(user.email)

    return UserWithToken(
        id=user.id,
        email=user.email,
        username=user.username,
        hashed_password=user.hashed_password,
        created_at=user.created_at,
        updated_at=user.updated_at,
        avatar=user.avatar,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        is_verified=user.is_verified,
        access_token=tokes.access_token,
        refresh_token=tokes.refresh_token,
    )


@router.get("/me/", response_model=UserSchema)
async def me(user: UserModel = Depends(jwt_bearer)):
    return user


@router.post("/refresh_token/", response_model=AccessTokenSchema)
async def refresh_token(request: RefreshTokenSchema, db: AsyncSession = Depends(get_async_session)):
    new_access_token = await JWTBearer.verify_refresh_token(request.refresh_token, db)

    if not new_access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    return AccessTokenSchema(access_token=new_access_token)

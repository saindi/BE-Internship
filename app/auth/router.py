from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_async_session
from auth.auth import jwt_bearer, JWTBearer
from auth.schemas import TokenSchema, LoginSchema, AccessTokenSchema, RefreshTokenSchema
from user.models.models import UserModel
from user.schemas import UserSchema

router = APIRouter(prefix='/auth')


@router.post("/login/", response_model=TokenSchema)
async def login(request: LoginSchema, db: AsyncSession = Depends(get_async_session)):
    user = await UserModel.get_by_fields(db, email=request.email)

    if not user or user.user_verification(request.password) == False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect login or password')

    return jwt_bearer.sign_jwt(user.email)


@router.get("/me/", response_model=UserSchema)
async def me(user: UserModel = Depends(jwt_bearer)):
    return user


@router.post("/refresh_token", response_model=AccessTokenSchema)
async def refresh_token(request: RefreshTokenSchema):
    new_access_token = JWTBearer.verify_refresh_token(request.refresh_token)

    if not new_access_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or expired refresh token")

    return AccessTokenSchema(access_token=new_access_token)

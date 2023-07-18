from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_async_session
from auth.auth import JWTBearer
from auth.schemas import TokenSchema, LoginSchema
from user.models import UserModel
from user.schemas import UserSchema

router = APIRouter(prefix='/auth')


@router.post("/login", response_model=TokenSchema)
async def signin(request: LoginSchema, db: AsyncSession = Depends(get_async_session)):
    user = await UserModel.get_by_fields(db, email=request.email)

    if not user or user.user_verification(request.password) == False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect login or password')

    return JWTBearer.sign_jwt(user.email)


@router.get("/me", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def me(user: list = Depends(JWTBearer())):
    return user

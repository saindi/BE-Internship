from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_async_session
from auth.auth import jwt_bearer
from auth.schemas import TokenSchema, LoginSchema
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

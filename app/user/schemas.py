from pydantic import BaseModel, EmailStr
from datetime import datetime
from pydantic_settings import SettingsConfigDict


class UserSchema(BaseModel):
    id: int
    email: EmailStr
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    model_config = SettingsConfigDict(from_attributes=True)


class UserData(BaseModel):
    email: EmailStr
    password: str


class SignInRequest(UserData):
    pass


class SignUpRequest(UserData):
    pass


class UserUpdateRequest(UserData):
    pass


class TokenSchema(BaseModel):
    access_token: str

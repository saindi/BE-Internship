from pydantic import BaseModel
from typing import List


class User(BaseModel):
    id: int
    email: str
    hashed_password: str
    registered_at: str
    is_active: bool
    is_superuser: bool
    is_verified: bool

    class Config:
        orm_mode = True


class SignInRequest(BaseModel):
    email: str
    password: str


class SignUpRequest(BaseModel):
    email: str
    password: str


class UserUpdateRequest(BaseModel):
    email: str
    password: str


class UsersListResponse(BaseModel):
    users: List[User]


class UserDetailResponse(BaseModel):
    user: User

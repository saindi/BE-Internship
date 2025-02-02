from datetime import datetime
from typing import Optional

from pydantic_core.core_schema import FieldValidationInfo
from pydantic import BaseModel, EmailStr, field_validator
from pydantic_settings import SettingsConfigDict

from auth.schemas import TokenSchema
from company.models.models import RoleEnum
from user.models.models import StatusEnum
from utils.hashing import Hasher


class UserSchema(BaseModel):
    id: int
    email: EmailStr
    username: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    avatar: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    model_config = SettingsConfigDict(from_attributes=True)


class UserWithToken(UserSchema, TokenSchema):
    pass


class UserWithRoleInCompany(UserSchema):
    role: RoleEnum


class UsersResponse(BaseModel):
    data: list[UserSchema]
    count_pages: int


class UserNewData(BaseModel):
    username: str
    password: str
    password_confirm: str

    @field_validator('password_confirm')
    def passwords_match(cls, v, info: FieldValidationInfo):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('passwords do not match')
        return v


class UserCreateRequest(UserNewData):
    email: EmailStr


class UserUpdateRequest(UserNewData):
    pass


class UserCreateData:
    username: str
    hashed_password: str

    def __init__(self, new_data: UserUpdateRequest):
        self.username = new_data.username
        self.hashed_password = Hasher.get_password_hash(new_data.password)

    def __iter__(self):
        return iter(vars(self).items())


class NotificationSchema(BaseModel):
    id: int
    id_user: int
    text: str
    status: StatusEnum
    created_at: datetime
    updated_at: datetime

    model_config = SettingsConfigDict(from_attributes=True)

    def dict(self, **kwargs):
        data = super().model_dump(**kwargs)

        data['status'] = data['status'].value
        data['created_at'] = data['created_at'].isoformat()
        data['updated_at'] = data['updated_at'].isoformat()

        return data

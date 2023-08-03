from datetime import datetime

from pydantic_core.core_schema import FieldValidationInfo
from pydantic import BaseModel, EmailStr, field_validator
from pydantic_settings import SettingsConfigDict

from user.models.models import StatusEnum
from utils.hashing import Hasher


class UserSchema(BaseModel):
    id: int
    email: EmailStr
    username: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    model_config = SettingsConfigDict(from_attributes=True)


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
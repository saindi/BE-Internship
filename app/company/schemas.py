from datetime import datetime

from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict

from user.schemas import UserSchema


class CompanySchema(BaseModel):
    id: int
    name: str
    description: str
    is_hidden: bool
    owner_id: int
    created_at: datetime
    updated_at: datetime

    owner: UserSchema

    model_config = SettingsConfigDict(from_attributes=True)


class CompanyData(BaseModel):
    name: str
    description: str


class CompanyCreateRequest(CompanyData):
    pass


class CompanyUpdateRequest(CompanyData):
    is_hidden: bool

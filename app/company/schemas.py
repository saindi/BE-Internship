from datetime import datetime
from typing import List

from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict

from company.models.models import RoleEnum


class CompanySchema(BaseModel):
    id: int
    name: str
    description: str
    is_hidden: bool
    created_at: datetime
    updated_at: datetime

    model_config = SettingsConfigDict(from_attributes=True)


class CompanyResponse(BaseModel):
    data: List[CompanySchema]
    count_pages: int


class CompanyData(BaseModel):
    name: str
    description: str


class CompanyCreateRequest(CompanyData):
    pass


class CompanyUpdateRequest(CompanyData):
    is_hidden: bool


class InvitationSchema(BaseModel):
    id: int
    id_company: int
    id_user: int
    created_at: datetime
    updated_at: datetime

    model_config = SettingsConfigDict(from_attributes=True)


class RequestSchema(BaseModel):
    id: int
    id_company: int
    id_user: int
    created_at: datetime
    updated_at: datetime

    model_config = SettingsConfigDict(from_attributes=True)


class RoleSchema(BaseModel):
    id_company: int
    id_user: int
    role: RoleEnum


class InviteUserRequest(BaseModel):
    user_id: int


class RequestToCompanyRequest(BaseModel):
    company_id: int

from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import jwt_bearer
from company.schemas import CompanySchema, CompanyCreateRequest, CompanyUpdateRequest
from db.database import get_async_session
from company.models import Company
from user.models import User

router = APIRouter(prefix='/company')


@router.get("/", response_model=List[CompanySchema], dependencies=[Depends(jwt_bearer)])
async def get_companies(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_async_session)):
    companies = await Company.get_by_fields(db, return_single=False, skip=skip, limit=limit, is_hidden=False)

    if not companies:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No records found')

    return companies


@router.get("/{company_id}/", response_model=CompanySchema, dependencies=[Depends(jwt_bearer)])
async def get_company_by_id(company_id: int, db: AsyncSession = Depends(get_async_session)):
    company = await Company.get_by_id(db, company_id)

    if company.is_hidden:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='This company is hidden')

    return company


@router.post("/",  response_model=CompanySchema, status_code=status.HTTP_201_CREATED)
async def create_company(
        request: CompanyCreateRequest,
        user: User = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    new_company = Company(**dict(request))

    await new_company.create(db, user.id)

    return new_company


@router.put("/{company_id}/", response_model=CompanySchema, status_code=status.HTTP_201_CREATED)
async def update_company(
        company_id: int,
        data: CompanyUpdateRequest,
        user: User = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await Company.get_by_id(db, company_id)

    if not company.user_can_edit(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='This user cannot change the company')

    await company.update(db, data)

    return company


@router.delete("/{company_id}/")
async def delete_company(
        company_id: int,
        user: User = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await Company.get_by_id(db, company_id)

    if not company.user_can_delete(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='This user cannot delete сompany')

    return await company.delete(db)

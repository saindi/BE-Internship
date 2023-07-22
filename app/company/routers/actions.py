from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import jwt_bearer
from company.schemas import InvitationSchema, RequestSchema, RoleSchema
from db.database import get_async_session
from company.models import Company, InvitationModel, RequestModel, RoleModel, RoleEnum
from user.models import User
from user.schemas import UserSchema

router = APIRouter(prefix='/company')


@router.get("/{company_id}/users/", response_model=List[UserSchema])
async def get_requests(
        company_id: int,
        skip: int = 0,
        limit: int = 100,
        user: User = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await Company.get_by_fields(db, skip=skip, limit=limit, id=company_id)

    if not company.is_owner(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No read permission')

    return company.users


@router.get("/{company_id}/kick/{user_id}")
async def kick_user(
        company_id: int,
        user_id: int,
        user: User = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await Company.get_by_id(db, company_id)
    kick_user = await User.get_by_id(db, user_id)
    kick_role = await RoleModel.get_by_fields(db, id_user=kick_user.id, id_company=company.id)

    if not kick_role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='This user is not in the company.')

    if not company.is_owner(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No kick permission.')

    if kick_role.role == RoleEnum.OWNER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='The owner of a company can not kick himself.')

    return await kick_role.delete(db)


@router.get("/{company_id}/invitations", response_model=List[InvitationSchema])
async def get_invitations(
        company_id: int,
        user: User = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await Company.get_by_id(db, company_id)

    if not company.is_owner(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No read permission')

    return company.invitations


@router.post("/{company_id}/invitation", response_model=InvitationSchema)
async def create_invitation(
        company_id: int,
        user_id: int,
        user: User = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await Company.get_by_id(db, company_id)
    new_member = await User.get_by_id(db, user_id)

    if not company.is_owner(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No create permission')

    invate = await company.add_invite_to_company(db, new_member)

    await invate.create(db)

    return invate


@router.delete("/{company_id}/invitation/{invite_id}")
async def delete_invitation(
        company_id: int,
        invite_id: int,
        user: User = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await Company.get_by_id(db, company_id)

    if not company.is_owner(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No create permission')

    invitation = await InvitationModel.get_by_id(db, invite_id)

    return await invitation.delete(db)


@router.get("/{company_id}/requests", response_model=List[RequestSchema])
async def get_requests(
        company_id: int,
        user: User = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await Company.get_by_id(db, company_id)

    if not company.is_owner(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No read permission')

    return company.requests


@router.get("/{company_id}/request/{request_id}/accept", response_model=RoleSchema)
async def get_requests(
        company_id: int,
        request_id: int,
        user: User = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await Company.get_by_id(db, company_id)

    if not company.is_owner(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No read permission')

    request = await RequestModel.get_by_id(db, request_id)

    new_role = RoleModel(id_user=request.id_user, id_company=request.id_company, role=RoleEnum.MEMBER)

    await new_role.create(db)

    return new_role


@router.get("/{company_id}/request/{request_id}/reject")
async def get_requests(
        company_id: int,
        request_id: int,
        user: User = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await Company.get_by_id(db, company_id)

    if not company.is_owner(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No read permission')

    request = await RequestModel.get_by_id(db, request_id)

    return await request.delete(db)

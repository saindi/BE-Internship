from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from auth.auth import jwt_bearer
from company.schemas import InvitationSchema, RequestSchema, RoleSchema
from db.database import get_async_session
from company.models.models import CompanyModel, InvitationModel, RequestModel, RoleModel, RoleEnum
from db.redis_actions import get_values_by_keys
from quiz.schemas import QuizSchema, ResultData
from user.models.models import UserModel
from user.schemas import UserSchema
from utils.generate_csv import generate_csv_data_as_results

router = APIRouter(prefix='/company')


@router.get("/{company_id}/owner/", response_model=UserSchema, dependencies=[Depends(jwt_bearer)])
async def get_owner_user(company_id: int, db: AsyncSession = Depends(get_async_session)):
    company = await CompanyModel.get_by_id(db, company_id)

    return company.get_owner()


@router.get("/{company_id}/admins/", response_model=List[UserSchema], dependencies=[Depends(jwt_bearer)])
async def get_admins(company_id: int, db: AsyncSession = Depends(get_async_session)):
    company = await CompanyModel.get_by_id(db, company_id)

    return company.get_admins()


@router.get("/{company_id}/admin/{user_id}/set/", response_model=RoleSchema)
async def set_admin(
        company_id: int,
        user_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await CompanyModel.get_by_id(db, company_id)

    if not company.is_owner(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No permission')

    role = await RoleModel.get_by_fields(db, id_company=company_id, id_user=user_id)

    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User not found in the company')

    await role.update(db, {'role': RoleEnum.ADMIN})

    return role


@router.get("/{company_id}/admin/{user_id}/remove/", response_model=RoleSchema)
async def remove_admin(
        company_id: int,
        user_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await CompanyModel.get_by_id(db, company_id)

    if not company.is_owner(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No permission')

    role = await RoleModel.get_by_fields(db, id_company=company_id, id_user=user_id)

    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User not found in the company')

    await role.update(db, {'role': RoleEnum.MEMBER})

    return role


@router.get("/{company_id}/users/", response_model=List[UserSchema])
async def get_users(
        company_id: int,
        skip: int = 0,
        limit: int = 100,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await CompanyModel.get_by_fields(db, skip=skip, limit=limit, id=company_id)

    if not company.is_owner(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No read permission')

    return company.users


@router.get("/{company_id}/kick/{user_id}/")
async def kick_user(
        company_id: int,
        user_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await CompanyModel.get_by_id(db, company_id)
    kick_user = await UserModel.get_by_id(db, user_id)
    kick_role = await RoleModel.get_by_fields(db, id_user=kick_user.id, id_company=company.id)

    if not kick_role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='This user is not in the company.')

    if not company.is_owner(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No kick permission.')

    if kick_role.role == RoleEnum.OWNER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='The owner of a company can not kick himself.')

    return await kick_role.delete(db)


@router.get("/{company_id}/invitations/", response_model=List[InvitationSchema])
async def get_invitations(
        company_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await CompanyModel.get_by_id(db, company_id)

    if not company.is_owner(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No read permission')

    return company.invitations


@router.post("/{company_id}/invitation/", response_model=InvitationSchema, status_code=status.HTTP_201_CREATED)
async def create_invitation(
        company_id: int,
        user_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await CompanyModel.get_by_id(db, company_id)
    new_member = await UserModel.get_by_id(db, user_id)

    if not company.is_owner(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No create permission')

    invate = await company.add_invite_to_company(db, new_member)

    await invate.create(db)

    return invate


@router.delete("/{company_id}/invitation/{invite_id}/")
async def delete_invitation(
        company_id: int,
        invite_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await CompanyModel.get_by_id(db, company_id)

    if not company.is_owner(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No create permission')

    invitation = await InvitationModel.get_by_id(db, invite_id)

    return await invitation.delete(db)


@router.get("/{company_id}/requests/", response_model=List[RequestSchema])
async def get_requests(
        company_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await CompanyModel.get_by_id(db, company_id)

    if not company.is_owner(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No read permission')

    return company.requests


@router.get("/{company_id}/request/{request_id}/accept/", response_model=RoleSchema)
async def accept_request(
        company_id: int,
        request_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await CompanyModel.get_by_id(db, company_id)

    if not company.is_owner(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No read permission')

    request = await RequestModel.get_by_id(db, request_id)

    new_role = RoleModel(id_user=request.id_user, id_company=request.id_company, role=RoleEnum.MEMBER)

    await new_role.create(db)

    return new_role


@router.get("/{company_id}/request/{request_id}/reject/")
async def reject_request(
        company_id: int,
        request_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await CompanyModel.get_by_id(db, company_id)

    if not company.is_owner(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No read permission')

    request = await RequestModel.get_by_id(db, request_id)

    return await request.delete(db)


@router.get("/{company_id}/quizzes/", response_model=List[QuizSchema])
async def get_quizzes(
        company_id: int,
        skip: int = 0,
        limit: int = 100,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await CompanyModel.get_by_id(db, company_id)

    if not company.is_user_in_company(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No read permission')

    return company.quizzes[skip:limit]


@router.get("/{company_id}/results/", response_model=List[ResultData])
async def get_results(
        company_id: int,
        skip: int = 0,
        limit: int = 100,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await CompanyModel.get_by_id(db, company_id)

    if not company.user_entitled_quiz(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No read permission')

    results = await get_values_by_keys(id_company=company_id)

    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Results not found")

    return results[skip:limit]


@router.get("/{company_id}/results/csv/")
async def get_results_csv(
        company_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await CompanyModel.get_by_id(db, company_id)

    if not company.user_entitled_quiz(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No read permission')

    results = await get_values_by_keys(id_company=company_id)

    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Results not found")

    csv = generate_csv_data_as_results([ResultData.model_validate(result).model_dump() for result in results])

    return StreamingResponse(csv, media_type="multipart/form-data",
                             headers={"Content-Disposition": "attachment; filename=data.csv"})


@router.get("/{company_id}/results_user/{user_id}/", response_model=List[ResultData])
async def get_user_results(
        company_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await CompanyModel.get_by_id(db, company_id)

    if not company.is_user_in_company(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No read permission')

    results = await get_values_by_keys(id_user=user_id, id_company=company_id)

    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Results not found")

    return results[skip:limit]


@router.get("/{company_id}/results_user/{user_id}/csv/")
async def get_user_results_csv(
        company_id: int,
        user_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await CompanyModel.get_by_id(db, company_id)

    if not company.is_user_in_company(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No read permission')

    results = await get_values_by_keys(id_user=user_id, id_company=company_id)

    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Results not found")

    csv = generate_csv_data_as_results([ResultData.model_validate(result).model_dump() for result in results])

    return StreamingResponse(csv, media_type="multipart/form-data",
                             headers={"Content-Disposition": "attachment; filename=data.csv"})


@router.get("/{company_id}/results_quiz/{quiz_id}/", response_model=List[ResultData])
async def get_results_quiz(
        company_id: int,
        quiz_id: int,
        skip: int = 0,
        limit: int = 100,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await CompanyModel.get_by_id(db, company_id)

    if not company.is_user_in_company(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No read permission')

    results = await get_values_by_keys(id_company=company_id, id_quiz=quiz_id)

    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Results not found")

    return results[skip:limit]


@router.get("/{company_id}/results_quiz/{quiz_id}/csv/")
async def get_results_quiz_csv(
        company_id: int,
        quiz_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await CompanyModel.get_by_id(db, company_id)

    if not company.is_user_in_company(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No read permission')

    results = await get_values_by_keys(id_company=company_id, id_quiz=quiz_id)

    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Results not found")

    csv = generate_csv_data_as_results([ResultData.model_validate(result).model_dump() for result in results])

    return StreamingResponse(csv, media_type="multipart/form-data",
                             headers={"Content-Disposition": "attachment; filename=data.csv"})

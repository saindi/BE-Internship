from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import StreamingResponse

from auth.auth import jwt_bearer
from company.models.models import CompanyModel, RequestModel, RoleModel, InvitationModel, RoleEnum
from company.schemas import RequestSchema, InvitationSchema, RoleSchema, CompanySchema
from db.database import get_async_session
from db.redis_actions import get_values_by_keys, get_value_by_keys
from quiz.models.models import AverageScoreGlobalModel, AverageScoreCompanyModel, ResultTestModel
from quiz.schemas import CompanyRatingSchema, GlobalRatingSchema, ResultData
from user.models.models import UserModel
from utils.generate_csv import generate_csv_data_as_result, generate_csv_data_as_results

router = APIRouter(prefix='/user')


@router.get("/companies/", response_model=List[CompanySchema])
async def get_requests(skip: int = 0, limit: int = 100, user: UserModel = Depends(jwt_bearer)):
    return user.companies[skip:limit]


@router.get("/company/{company_id}/exit/", response_model=List[CompanySchema])
async def exit_from_company(
        company_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await CompanyModel.get_by_id(db, company_id)
    role = await RoleModel.get_by_fields(db, id_company=company.id, id_user=user.id)

    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You're not a member of the company")

    if role.role == RoleEnum.OWNER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Owner can't get out of his company")

    return await role.delete(db)


@router.get("/requests/", response_model=List[RequestSchema])
async def get_requests(user: UserModel = Depends(jwt_bearer)):
    return user.requests


@router.post("/request/", response_model=RequestSchema, status_code=status.HTTP_201_CREATED)
async def create_request(
        company_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await CompanyModel.get_by_id(db, company_id)

    request = await user.add_request_to_company(db, company)

    return request


@router.delete("/request/{request_id}/")
async def delete_invitation(
        request_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    request = await RequestModel.get_by_id(db, request_id)

    if request.id_user != user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can't delete this request")

    return await request.delete(db)


@router.get("/invitations/", response_model=List[InvitationSchema])
async def get_invitations(user: UserModel = Depends(jwt_bearer)):
    return user.invitations


@router.get("/invitation/{invite_id}/accept/", response_model=RoleSchema)
async def accept_invitation(
        invite_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    invite = await InvitationModel.get_by_fields(db, id_user=user.id, id=invite_id)

    if not invite:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invite not found")

    role = RoleModel(id_user=invite.id_user, id_company=invite.id_company, role=RoleEnum.MEMBER)

    await role.create(db)

    return role


@router.get("/invitation/{invite_id}/reject/")
async def reject_invitation(
        invite_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    invite = await InvitationModel.get_by_fields(db, id_user=user.id, id=invite_id)

    if not invite:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invite not found")

    return await invite.delete(db)


@router.get("/test_results/", response_model=List[ResultData])
async def get_results(user: UserModel = Depends(jwt_bearer)):
    results = await get_values_by_keys(id_user=user.id)

    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Results not found")

    return results


@router.get("/test_results/csv/")
async def get_results_csv(user: UserModel = Depends(jwt_bearer)):
    results = await get_values_by_keys(id_user=user.id)

    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Results not found")

    csv = generate_csv_data_as_results([ResultData.model_validate(result).model_dump() for result in results])

    return StreamingResponse(csv, media_type="multipart/form-data",
                             headers={"Content-Disposition": "attachment; filename=data.csv"})


@router.get("/test_result/{result_test_id}/", response_model=ResultData)
async def get_result_by_id(
        result_test_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    result_from_redis = await get_value_by_keys(result_test=result_test_id, id_user=user.id)

    if result_from_redis:
        return result_from_redis

    result = await ResultTestModel.get_by_fields(db, id_user=user.id, id=result_test_id)

    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Result not found")

    return result


@router.get("/test_result/{result_test_id}/csv/")
async def get_result_csv(
        result_test_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    result_from_redis = await get_value_by_keys(id_user=user.id, result_test=result_test_id)

    if not result_from_redis:
        result = await ResultTestModel.get_by_fields(db, id_user=user.id, id=result_test_id)

        if not result:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Result not found")

    csv = generate_csv_data_as_result(ResultData.model_validate(result).model_dump())

    return StreamingResponse(csv, media_type="multipart/form-data",
                             headers={"Content-Disposition": "attachment; filename=data.csv"})


@router.get("/global_rating/", response_model=GlobalRatingSchema)
async def get_global_rating(
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    global_rating = await AverageScoreGlobalModel.get_by_fields(db, id_user=user.id)

    if not global_rating:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You haven't taken the quizzes yet")

    return global_rating


@router.get("/company_rating/", response_model=List[CompanyRatingSchema])
async def get_company_rating(
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company_rating = await AverageScoreCompanyModel.get_by_fields(db, return_single=False, id_user=user.id)

    if not company_rating:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You haven't taken the quizzes yet")

    return company_rating

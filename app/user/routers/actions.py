from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import StreamingResponse

from auth.auth import jwt_bearer
from company.models.models import CompanyModel, RequestModel, RoleModel, InvitationModel, RoleEnum
from company.schemas import RequestSchema, InvitationSchema, RoleSchema, CompanySchema, RequestToCompanyRequest
from db.database import get_async_session
from db.redis_actions import get_values_by_keys, get_value_by_keys
from quiz.models.models import ResultTestModel
from analytic.models.models import AverageScoreCompanyModel, AverageScoreGlobalModel
from quiz.schemas import ResultData
from analytic.schemas import GlobalRatingSchema, CompanyRatingSchema
from user.models.models import UserModel, FileNameEnum, NotificationModel, StatusEnum
from user.schemas import NotificationSchema
from utils.generate_csv import generate_csv_data_as_result, generate_csv_data_as_results
from analytic.routers.user import router as user_analytic_router

router = APIRouter(prefix='/user')

@router.get("/{user_id}/companies/", response_model=List[CompanySchema])
async def get_requests(
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    if not user.can_read(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No permission")

    return (await user.companies(db))[skip:limit]


@router.get("/{user_id}/company/{company_id}/exit/")
async def exit_from_company(
        user_id: int,
        company_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    if not user.can_delete(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No permission")

    company = await CompanyModel.get_by_id(db, company_id)
    role = await RoleModel.get_by_fields(db, id_company=company.id, id_user=user_id)

    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You're not a member of the company")

    if role.role == RoleEnum.OWNER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Owner can't get out of his company")

    return await role.delete(db)


@router.get("/{user_id}/request/", response_model=List[RequestSchema])
async def get_requests(user_id: int, user: UserModel = Depends(jwt_bearer), db: AsyncSession = Depends(get_async_session)):
    if not user.can_read(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No permission")

    return await user.requests(db)


@router.post("/{user_id}/request/", response_model=RequestSchema, status_code=status.HTTP_201_CREATED)
async def create_request(
        user_id: int,
        request: RequestToCompanyRequest,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    if not user.can_edit(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No permission")

    company = await CompanyModel.get_by_id(db, request.company_id)

    request = await user.add_request_to_company(db, company)

    return request


@router.delete("/{user_id}/request/{request_id}/")
async def delete_invitation(
        user_id: int,
        request_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    if not user.can_delete(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No permission")

    request = await RequestModel.get_by_id(db, request_id)

    if request.id_user != user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You can't delete this request")

    return await request.delete(db)


@router.get("/{user_id}/invitations/", response_model=List[InvitationSchema])
async def get_invitations(user_id: int, user: UserModel = Depends(jwt_bearer), db: AsyncSession = Depends(get_async_session)):
    if not user.can_read(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No permission")

    return await user.invitations(db)


@router.get("/{user_id}/invitation/{invite_id}/accept/", response_model=RoleSchema)
async def accept_invitation(
        user_id: int,
        invite_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    if not user.can_edit(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No permission")

    invite = await InvitationModel.get_by_fields(db, id_user=user_id, id=invite_id)

    if not invite:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invite not found")

    role = RoleModel(id_user=invite.id_user, id_company=invite.id_company, role=RoleEnum.MEMBER)

    await role.create(db)

    await invite.delete(db)

    return role


@router.get("/{user_id}/invitation/{invite_id}/reject/")
async def reject_invitation(
        user_id: int,
        invite_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    if not user.can_edit(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No permission")

    invite = await InvitationModel.get_by_fields(db, id_user=user_id, id=invite_id)

    if not invite:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invite not found")

    return await invite.delete(db)


@router.get("/{user_id}/test_results/", response_model=List[ResultData])
async def get_results(
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        user: UserModel = Depends(jwt_bearer)
):
    if not user.can_read(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No permission")

    results = await get_values_by_keys(id_user=user_id)

    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Results not found")

    return results[skip:limit]


@router.get("/{user_id}/test_results/csv/")
async def get_results_csv(user_id, user: UserModel = Depends(jwt_bearer)):
    if not user.can_read(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No permission")

    results = await get_values_by_keys(id_user=user_id)

    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Results not found")

    csv = generate_csv_data_as_results([ResultData.model_validate(result).model_dump() for result in results])

    return StreamingResponse(csv, media_type="multipart/form-data",
                             headers={"Content-Disposition": f"attachment; filename={FileNameEnum.ALL_RESULTS_USER.value}"})


@router.get("/{user_id}/test_result/{result_test_id}/", response_model=ResultData)
async def get_result_by_id(
        user_id: int,
        result_test_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    if not user.can_read(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No permission")

    result_from_redis = await get_value_by_keys(result_test=result_test_id, id_user=user_id)

    if result_from_redis:
        return result_from_redis

    result = await ResultTestModel.get_by_fields(db, id_user=user_id, id=result_test_id)

    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Result not found")

    return result


@router.get("/{user_id}/test_result/{result_test_id}/csv/")
async def get_result_csv(
        user_id: int,
        result_test_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    if not user.can_read(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No permission")

    result_from_redis = await get_value_by_keys(id_user=user_id, result_test=result_test_id)

    if not result_from_redis:
        result = await ResultTestModel.get_by_fields(db, id_user=user_id, id=result_test_id)

        if not result:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Result not found")

    csv = generate_csv_data_as_result(ResultData.model_validate(result).model_dump())

    return StreamingResponse(csv, media_type="multipart/form-data",
                             headers={"Content-Disposition": f"attachment; filename={FileNameEnum.TEST_RESULT.value}"})


@router.get("/{user_id}/global_rating/", response_model=GlobalRatingSchema)
async def get_global_rating(
        user_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    if not user.can_read(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No permission")

    global_rating = await AverageScoreGlobalModel.get_by_fields(db, id_user=user_id)

    if not global_rating:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You haven't taken the quizzes yet")

    return global_rating


@router.get("/{user_id}/company_rating/", response_model=List[CompanyRatingSchema])
async def get_company_rating(
        user_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    if not user.can_read(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No permission")

    company_rating = await AverageScoreCompanyModel.get_by_fields(db, return_single=False, id_user=user_id)

    if not company_rating:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You haven't taken the quizzes yet")

    return company_rating


@router.get("/{user_id}/notifications/", response_model=List[NotificationSchema])
async def get_notifications(
        user_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    if not user.can_read(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No permission")

    notifications = await NotificationModel.get_by_fields(db, return_single=False, id_user=user_id)

    return notifications


@router.delete("/{user_id}/notifications/delete_read/")
async def delete_read_notifications(
        user_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    if not user.can_read(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No permission")

    return await NotificationModel.delete_read(db, user.id)


@router.put("/{user_id}/notification/{notification_id}/mark_read/", response_model=NotificationSchema)
async def mark_read_notification(
        user_id: int,
        notification_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    if not user.can_read(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No permission")

    notification = await NotificationModel.get_by_fields(db, id_user=user_id, id=notification_id)

    if not notification:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Notification not found")

    await notification.update(db, {'status': StatusEnum.READ.value})

    return notification


router.include_router(user_analytic_router)

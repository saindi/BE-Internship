from typing import List

from fastapi import Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from analytic.schemas import QuizAnalyticByTime, UserLastPassQuiz
from auth.auth import jwt_bearer
from company.models.models import CompanyModel
from db.database import get_async_session
from quiz.models.models import ResultTestModel
from quiz.schemas import ResultTestSchema
from user.models.models import UserModel
from utils.analytic import avarage_quiz_score_by_time, company_users_last_pass_quizzes
from company.routers.actions import router


@router.get("/{company_id}/users_analytic/", response_model=List[QuizAnalyticByTime])
async def get_users_analytic(
        company_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await CompanyModel.get_by_id(db, company_id)

    if not company.is_user_manager(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No permission')

    results = await ResultTestModel.get_by_fields(db, return_single=False, id_company=company.id)

    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User haven't taken the quizzes yet")

    analytic = avarage_quiz_score_by_time([ResultTestSchema.model_validate(result).model_dump() for result in results])

    return analytic


@router.get("/{company_id}/user_analytic/{user_id}/", response_model=List[QuizAnalyticByTime])
async def get_user_analytic(
        company_id: int,
        user_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await CompanyModel.get_by_id(db, company_id)

    if not company.is_user_manager(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No permission')

    results = await ResultTestModel.get_by_fields(db, return_single=False, id_user=user_id, id_company=company.id)

    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User haven't taken the quizzes yet")

    analytic = avarage_quiz_score_by_time([ResultTestSchema.model_validate(result).model_dump() for result in results])

    return analytic


@router.get("/{company_id}/users_last_pass_quizzes/", response_model=List[UserLastPassQuiz])
async def get_date_last_pass_company_quizzes(
        company_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await CompanyModel.get_by_id(db, company_id)

    if not company.is_user_manager(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No permission')

    results = await ResultTestModel.get_by_fields(db, return_single=False, id_company=company_id)

    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User haven't taken the quizzes yet")

    analytic = company_users_last_pass_quizzes([ResultTestSchema.model_validate(result).model_dump() for result in results])

    return analytic

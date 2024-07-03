from typing import List

from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from analytic.models.models import AverageScoreGlobalModel
from analytic.schemas import GlobalRatingSchema, QuizAnalyticByTime, LastPassQuizzes
from auth.auth import jwt_bearer
from db.database import get_async_session
from quiz.models.models import ResultTestModel, QuizModel
from quiz.schemas import ResultTestSchema
from user.models.models import UserModel
from utils.analytic import avarage_quiz_score_by_time, user_last_pass_quizzes

router = APIRouter(tags=['User analytic'])


@router.get("/{user_id}/global_rating_analytic/", response_model=GlobalRatingSchema, dependencies=[Depends(jwt_bearer)])
async def get_user_global_rating_analytic(
        user_id: int,
        db: AsyncSession = Depends(get_async_session)
):
    global_rating = await AverageScoreGlobalModel.get_by_fields(db, id_user=user_id)

    if not global_rating:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User haven't taken the quizzes yet")

    return global_rating


@router.get("/{user_id}/quiz_analytic/{quiz_id}/", response_model=List[QuizAnalyticByTime])
async def get_quiz_analytic(
        user_id: int,
        quiz_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    if not user.can_read(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No permission")

    results = await ResultTestModel.get_by_fields(db, return_single=False, id_user=user_id, id_quiz=quiz_id)

    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User haven't taken the quizzes yet")

    analytic = avarage_quiz_score_by_time([ResultTestSchema.model_validate(result).model_dump() for result in results])

    return analytic


@router.get("/{user_id}/last_pass_quizzes/")
async def get_date_last_pass_quizzes(
        user_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    if not user.can_read(user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No permission")

    results = await ResultTestModel.get_by_fields(db, return_single=False, id_user=user_id)

    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User haven't taken the quizzes yet")

    quizzes = {}
    for result in results:
        quiz = await QuizModel.get_by_id(db, result.id_quiz)
        quizzes[quiz.id] = quiz

    analytic = user_last_pass_quizzes(
        [ResultTestSchema.model_validate(result).model_dump() for result in results],
        quizzes
    )

    return analytic

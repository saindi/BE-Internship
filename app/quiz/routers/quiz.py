from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import jwt_bearer
from db.database import get_async_session
from company.models.models import CompanyModel
from quiz.schemas import (
    QuizSchema,
    QuizData,
    QuizUpdate,
    QuestionData,
    QuizWithQuestion,
    PassTestRequest,
    ResultTestSchema
)
from quiz.models.models import QuizModel
from user.models.models import UserModel

router = APIRouter(prefix='/quiz')


@router.get("/{quiz_id}/", response_model=QuizWithQuestion)
async def get_quiz(quiz_id: int, user: UserModel = Depends(jwt_bearer), db: AsyncSession = Depends(get_async_session)):
    quiz = await QuizModel.get_by_id(db, quiz_id)

    if not quiz.company.is_user_in_company(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='A user cannot take quizzes from outside their company')

    return quiz


@router.post("/{company_id}/", response_model=QuizSchema, status_code=status.HTTP_201_CREATED)
async def create_quiz(
        company_id: int,
        data: QuizData,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    company = await CompanyModel.get_by_id(db, company_id)

    if not company.user_entitled_quiz(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No create permission')

    quiz = QuizModel(name=data.name, description=data.description, count_day=data.count_day, id_company=company.id)

    await quiz.create_with_questions(db, data)

    return quiz


@router.delete("/{quiz_id}/")
async def delete_quiz(quiz_id: int, user: UserModel = Depends(jwt_bearer), db: AsyncSession = Depends(get_async_session)):
    quiz = await QuizModel.get_by_id(db, quiz_id)

    if not quiz.company.user_entitled_quiz(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No delete permission')

    return await quiz.delete(db)


@router.put("/{quiz_id}/update_info/", response_model=QuizSchema, status_code=status.HTTP_201_CREATED)
async def update_info_quiz(
        quiz_id: int,
        data: QuizUpdate,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    quiz = await QuizModel.get_by_id(db, quiz_id)

    if not quiz.company.user_entitled_quiz(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No update permission')

    await quiz.update(db, data)

    return quiz


@router.post("/{quiz_id}/add_question/", response_model=QuizWithQuestion, status_code=status.HTTP_201_CREATED)
async def add_question_to_quiz(
        quiz_id: int,
        data: QuestionData,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    quiz = await QuizModel.get_by_id(db, quiz_id)

    if not quiz.company.user_entitled_quiz(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No update permission')

    await quiz.add_question(db, data)

    return quiz


@router.post("/{quiz_id}/pass_test/", response_model=ResultTestSchema, status_code=status.HTTP_201_CREATED)
async def pass_test(
        quiz_id: int,
        data: PassTestRequest,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    quiz = await QuizModel.get_by_id(db, quiz_id)

    if not quiz.company.is_user_in_company(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='A user cannot take quizzes from outside their company')

    result = await quiz.pass_test(db, user, data.answers)

    return result

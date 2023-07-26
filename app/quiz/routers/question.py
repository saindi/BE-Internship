from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import jwt_bearer
from db.database import get_async_session
from quiz.schemas import QuestionData, QuestionWithAnswer
from quiz.models import QuestionModel
from user.models import UserModel

router = APIRouter(prefix='/question')


@router.put("/{question_id}/", response_model=QuestionWithAnswer, status_code=status.HTTP_201_CREATED)
async def update_question(
        question_id: int,
        data: QuestionData,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    question = await QuestionModel.get_by_id(db, question_id)

    if not question.quiz.company.user_entitled_quiz(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No update permission')

    await question.update_with_answers(db, data)

    return question


@router.delete("/{question_id}/")
async def delete_question(
        question_id: int,
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    question = await QuestionModel.get_by_id(db, question_id)

    if not question.quiz.company.user_entitled_quiz(user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='No delete permission')

    return await question.delete(db)

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class IdWithUser(BaseModel):
    id: int
    id_user: int
    created_at: datetime
    updated_at: datetime


class GlobalRatingSchema(IdWithUser):
    rating: float


class CompanyRatingSchema(GlobalRatingSchema):
    id_company: int


class QuizAnalyticByTime(BaseModel):
    rating: float
    date: date


class LastPassQuizzes(BaseModel):
    id_quiz: int
    date_last_pass: datetime


class UserLastPassQuiz(BaseModel):
    id_user: int
    email: Optional[EmailStr]
    username: Optional[str]
    quiz_name: Optional[str]
    date_last_pass: datetime

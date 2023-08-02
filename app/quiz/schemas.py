from datetime import datetime
from typing import List

from pydantic import BaseModel, field_validator, conint
from pydantic_settings import SettingsConfigDict


class AnswerSchema(BaseModel):
    id: int
    answer: str
    id_question: int
    is_correct: bool
    created_at: datetime
    updated_at: datetime

    model_config = SettingsConfigDict(from_attributes=True)


class QuestionSchema(BaseModel):
    id: int
    question: str
    id_quiz: int
    created_at: datetime
    updated_at: datetime

    model_config = SettingsConfigDict(from_attributes=True)


class QuestionWithAnswer(QuestionSchema):
    answers: List[AnswerSchema]


class QuizSchema(BaseModel):
    id: int
    name: str
    description: str
    count_day: conint(gt=0)
    id_company: int
    created_at: datetime
    updated_at: datetime

    model_config = SettingsConfigDict(from_attributes=True)


class QuizWithQuestion(QuizSchema):
    questions: List[QuestionWithAnswer]


class QuizUpdate(BaseModel):
    name: str
    description: str
    count_day: conint(gt=0)


class AnswerData(BaseModel):
    answer: str
    is_correct: bool


class QuestionData(BaseModel):
    question: str

    answers: List[AnswerData]

    @field_validator('answers')
    def validate_questions(cls, answers):
        if len(answers) < 2:
            raise ValueError("The 'answers' attribute must have at least 2 elements.")
        return answers


class QuizData(BaseModel):
    name: str
    description: str
    count_day: conint(gt=0)

    questions: List[QuestionData]

    @field_validator('questions')
    def validate_questions(cls, questions):
        if len(questions) < 2:
            raise ValueError("The 'questions' attribute must have at least 2 elements.")
        return questions


class PassTestRequest(BaseModel):
    answers: List[List[int]]


class IdWithUser(BaseModel):
    id: int
    id_user: int
    created_at: datetime
    updated_at: datetime


class ResultTestSchema(IdWithUser):
    count_correct_answers: int
    count_questions: int
    id_company: int
    id_quiz: int

    model_config = SettingsConfigDict(from_attributes=True)


class UserAnswer(BaseModel):
    answer: str

    model_config = SettingsConfigDict(from_attributes=True)


class ResultQuestion(BaseModel):
    question: str
    answer_is_correct: bool
    user_answers: List[str]

    model_config = SettingsConfigDict(from_attributes=True)

    @field_validator('user_answers', mode='before')
    def validate_user_answers(cls, user_answers):
        from quiz.models.models import UserAnswerModel

        if not user_answers:
            raise ValueError("Not such user_answers")

        if isinstance(user_answers[0], UserAnswerModel):
            return [answer.answer for answer in user_answers]

        return user_answers


class ResultData(BaseModel):
    id: int
    id_user: int
    id_company: int
    id_quiz: int
    created_at: str

    questions: List[ResultQuestion]

    model_config = SettingsConfigDict(from_attributes=True)

    @field_validator('created_at', mode='before')
    def validate_created_at(cls, created_at):
        if not created_at:
            raise ValueError("Not such created_at")

        if isinstance(created_at, datetime):
            return created_at.isoformat()

        return created_at

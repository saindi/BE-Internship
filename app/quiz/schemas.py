from datetime import datetime
from typing import List

from pydantic import BaseModel, field_validator
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
    count_day: int
    id_company: int
    created_at: datetime
    updated_at: datetime

    model_config = SettingsConfigDict(from_attributes=True)


class QuizWithQuestion(QuizSchema):
    questions: List[QuestionWithAnswer]


class QuizUpdate(BaseModel):
    name: str
    description: str
    count_day: int


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
    count_day: int

    questions: List[QuestionData]

    @field_validator('questions')
    def validate_questions(cls, questions):
        if len(questions) < 2:
            raise ValueError("The 'questions' attribute must have at least 2 elements.")
        return questions

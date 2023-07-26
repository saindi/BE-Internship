from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from db.models import BaseModel
from quiz.crud import QuestionCrud, QuizCrud


class AnswerModel(BaseModel):
    __tablename__ = "answer"

    answer = Column(String, nullable=False)
    id_question = Column(Integer, ForeignKey("question.id"), nullable=False)
    is_correct = Column(Boolean, nullable=False)

    question = relationship("QuestionModel", back_populates="answers", lazy="subquery")


class QuestionModel(BaseModel, QuestionCrud):
    __tablename__ = "question"

    question = Column(String, nullable=False)
    id_quiz = Column(Integer, ForeignKey("quiz.id"), nullable=False)

    quiz = relationship("QuizModel", back_populates="questions", lazy="subquery")
    answers = relationship("AnswerModel", cascade="all, delete-orphan", back_populates="question", lazy="subquery")


class QuizModel(BaseModel, QuizCrud):
    __tablename__ = "quiz"

    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    count_day = Column(Integer, nullable=False)
    id_company = Column(Integer, ForeignKey("company.id"), nullable=False)

    company = relationship("CompanyModel", back_populates="quizzes", lazy="subquery")
    questions = relationship("QuestionModel", cascade="all, delete-orphan", back_populates="quiz", lazy="subquery")

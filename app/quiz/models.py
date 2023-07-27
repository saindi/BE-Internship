from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship

from db.models import BaseModel
from quiz.crud import QuestionCrud, QuizCrud


class ResultTestModel(BaseModel):
    __tablename__ = "resul_test"

    count_correct_answers = Column(Integer, nullable=False)
    count_questions = Column(Integer, nullable=False)
    id_user = Column(Integer, ForeignKey("user.id"), nullable=False)
    id_company = Column(Integer, ForeignKey("company.id"), nullable=False)
    id_quiz = Column(Integer, ForeignKey("quiz.id"), nullable=False)


class AverageScoreCompanyModel(BaseModel):
    __tablename__ = "average_score_company"

    id_user = Column(Integer, ForeignKey("user.id"), nullable=False)
    id_company = Column(Integer, ForeignKey("company.id"), nullable=False)
    rating = Column(Float, nullable=False)


class AverageScoreGlobalModel(BaseModel):
    __tablename__ = "average_score_global"

    id_user = Column(Integer, ForeignKey("user.id"), nullable=False, unique=True)
    rating = Column(Float, nullable=False)


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

from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship

from db.models import BaseModel
from quiz.models.crud import QuestionCrud, QuizCrud, AverageScoreCompanyCrud, AverageScoreGlobalCrud, ResultTestCrud, \
    ResultQuestionCrud


class AverageScoreCompanyModel(BaseModel, AverageScoreCompanyCrud):
    __tablename__ = "average_score_company"

    id_user = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    id_company = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Float, nullable=False)


class AverageScoreGlobalModel(BaseModel, AverageScoreGlobalCrud):
    __tablename__ = "average_score_global"

    id_user = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True)
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
    results = relationship("ResultTestModel", cascade="all, delete-orphan", lazy="subquery")


class ResultTestModel(BaseModel, ResultTestCrud):
    __tablename__ = "resul_test"

    count_correct_answers = Column(Integer, nullable=False)
    count_questions = Column(Integer, nullable=False)
    id_user = Column(Integer, ForeignKey("user.id"), nullable=False)
    id_company = Column(Integer, ForeignKey("company.id"), nullable=False)
    id_quiz = Column(Integer, ForeignKey("quiz.id"), nullable=False)

    questions = relationship("ResultQuestionModel", cascade="all, delete-orphan", lazy="subquery")


class ResultQuestionModel(BaseModel, ResultQuestionCrud):
    __tablename__ = "result_question"

    id_result = Column(Integer, ForeignKey("resul_test.id"), nullable=False)
    question = Column(String, nullable=False)
    answer_is_correct = Column(Boolean, nullable=False)

    user_answers = relationship("UserAnswerModel", cascade="all, delete-orphan", lazy="subquery")


class UserAnswerModel(BaseModel):
    __tablename__ = "user_answer"

    answer = Column(String, nullable=False)
    id_result_question = Column(Integer, ForeignKey("result_question.id"), nullable=False)
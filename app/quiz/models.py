from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from db.models import BaseModel


class AnswerModel(BaseModel):
    __tablename__ = "answer"

    answer = Column(String, nullable=False)
    id_question = Column(Integer, ForeignKey("question.id"), nullable=False)
    is_correct = Column(Boolean, nullable=False)

    question = relationship("QuestionModel", back_populates="answers", lazy="subquery")


class QuestionModel(BaseModel):
    __tablename__ = "question"

    question = Column(String, nullable=False)
    id_quiz = Column(Integer, ForeignKey("quiz.id"), nullable=False)

    quiz = relationship("QuizModel", back_populates="questions", lazy="subquery")
    answers = relationship("AnswerModel", cascade="all, delete-orphan", back_populates="question", lazy="subquery")

    async def create(self, db, data):
        await super().create(db)

        for answer in data:
            new_answer = AnswerModel(answer=answer.answer, id_question=self.id, is_correct=answer.is_correct)

            await new_answer.create(db)

        await db.refresh(self)

    async def update_with_answers(self, db, data):
        await self.update(db, {'question': data.question})

        for answer in self.answers:
            await answer.delete(db)

        for answer in data.answers:
            new_answer = AnswerModel(answer=answer.answer, id_question=self.id, is_correct=answer.is_correct)

            await new_answer.create(db)

        await db.refresh(self)



class QuizModel(BaseModel):
    __tablename__ = "quiz"

    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    count_day = Column(Integer, nullable=False)
    id_company = Column(Integer, ForeignKey("company.id"), nullable=False)

    company = relationship("CompanyModel", back_populates="quizzes", lazy="subquery")
    questions = relationship("QuestionModel", cascade="all, delete-orphan", back_populates="quiz", lazy="subquery")

    async def create(self, db, data):
        await super().create(db)

        for question in data.questions:
            new_question = QuestionModel(question=question.question, id_quiz=self.id)

            await new_question.create(db, question.answers)

    async def add_question(self, db, data):
        new_question = QuestionModel(question=data.question, id_quiz=self.id)

        await new_question.create(db, data.answers)

        await db.refresh(self)

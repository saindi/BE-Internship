class QuestionCrud:
    async def create_with_answer(self, db, data):
        from quiz.models import AnswerModel

        await self.create(db)

        for answer in data:
            new_answer = AnswerModel(answer=answer.answer, id_question=self.id, is_correct=answer.is_correct)

            await new_answer.create(db)

        await db.refresh(self)

    async def update_with_answers(self, db, data):
        from quiz.models import AnswerModel

        await self.update(db, {'question': data.question})

        for answer in self.answers:
            await answer.delete(db)

        for answer in data.answers:
            new_answer = AnswerModel(answer=answer.answer, id_question=self.id, is_correct=answer.is_correct)

            await new_answer.create(db)

        await db.refresh(self)


class QuizCrud:
    async def create_with_questions(self, db, data):
        from quiz.models import QuestionModel

        await self.create(db)

        for question in data.questions:
            new_question = QuestionModel(question=question.question, id_quiz=self.id)

            await new_question.create_with_answer(db, question.answers)

    async def add_question(self, db, data):
        from quiz.models import QuestionModel

        new_question = QuestionModel(question=data.question, id_quiz=self.id)

        await new_question.create_with_answer(db, data.answers)

        await db.refresh(self)

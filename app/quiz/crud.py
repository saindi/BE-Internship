from fastapi import status, HTTPException

from quiz.schemas import ResultTestSchema


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

    def get_question_by_id(self, id):
        for question in self.questions:
            if question.id == id:
                return question

        return None

    def get_correct_answer_for_question(self, number) -> list:
        question = self.questions[number]

        return [i for i in range(len(question.answers)) if question.answers[i].is_correct]

    def validate_answers(self, answers):
        # Checking for correlation between the number of answers to questions and the questions themselves
        if len(answers) != len(self.questions):
            detail = 'The number of answers must be equal to the number of questions'
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

        for i in range(len(answers)):
            # Checking the number of answers to a question
            if len(answers[i]) > len(self.questions[i].answers) or len(answers[i]) == 0:
                detail = f'Error entering answers for a question {i}'
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

            # Checking for recurring issues
            if len(answers[i]) != len(set(answers[i])):
                detail = f'Question {i} repeats the answers'
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

            # Checking if the answer is correct
            for j in range(len(answers[i])):
                if answers[i][j] >= len(self.questions[i].answers) or answers[i][j] < 0:
                    detail = f'Error entering answers for a question {i} answer {j}'
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

        return answers

    async def pass_test(self, db, test_user, answers) -> ResultTestSchema:
        from quiz.models import ResultTestModel

        self.validate_answers(answers)

        count_correct_answers: int = 0

        for i in range(len(answers)):
            if set(answers[i]) == set(self.get_correct_answer_for_question(i)):
                count_correct_answers += 1

        result_test = ResultTestModel(
            id_user=test_user.id,
            id_quiz=self.id,
            id_company=self.company.id,
            count_correct_answers=count_correct_answers,
            count_questions=len(self.questions)
        )

        await result_test.create(db)

        await self.set_company_rating(db, test_user, self.company.id)
        await self.set_global_rating(db, test_user)

        return result_test

    @staticmethod
    async def set_company_rating(db, user, company_id):
        from quiz.models import AverageScoreCompanyModel, ResultTestModel

        results = await ResultTestModel.get_by_fields(db, return_single=False, id_user=user.id, id_company=company_id)

        sum_correct, count_questions = 0, 0
        for result in results:
            sum_correct += result.count_correct_answers
            count_questions += result.count_questions

        rating = sum_correct / count_questions

        average_score_company = await AverageScoreCompanyModel.get_by_fields(db, id_user=user.id, id_company=company_id)

        if average_score_company:
            await average_score_company.update(db, {'rating': rating})
        else:
            average_company = AverageScoreCompanyModel(id_user=user.id, id_company=company_id, rating=rating)
            await average_company.create(db)

    @staticmethod
    async def set_global_rating(db, user):
        from quiz.models import AverageScoreGlobalModel, ResultTestModel

        results = await ResultTestModel.get_by_fields(db, return_single=False, id_user=user.id)

        sum_correct, count_questions = 0, 0
        for result in results:
            sum_correct += result.count_correct_answers
            count_questions += result.count_questions

        rating = sum_correct / count_questions

        average_score_global = await AverageScoreGlobalModel.get_by_fields(db, id_user=user.id)

        if average_score_global:
            await average_score_global.update(db, {'rating': rating})
        else:
            average_company = AverageScoreGlobalModel(id_user=user.id, rating=rating)
            await average_company.create(db)

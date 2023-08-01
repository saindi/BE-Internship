from sqlalchemy.ext.asyncio import AsyncSession

from utils.rating_calculation import get_rating


class AverageScoreCompanyCrud:
    @staticmethod
    async def set_company_rating(db: AsyncSession, user, company_id: int):
        from quiz.models.models import ResultTestModel
        from analytic.models.models import AverageScoreCompanyModel

        results = await ResultTestModel.get_by_fields(db, return_single=False, id_user=user.id, id_company=company_id)

        rating = get_rating(results)

        average_score_company = await AverageScoreCompanyModel.get_by_fields(db, id_user=user.id, id_company=company_id)

        if average_score_company:
            await average_score_company.update(db, {'rating': rating})
        else:
            average_company = AverageScoreCompanyModel(id_user=user.id, id_company=company_id, rating=rating)
            await average_company.create(db)


class AverageScoreGlobalCrud:
    @staticmethod
    async def set_global_rating(db: AsyncSession, user):
        from quiz.models.models import ResultTestModel
        from analytic.models.models import AverageScoreGlobalModel

        results = await ResultTestModel.get_by_fields(db, return_single=False, id_user=user.id)

        rating = get_rating(results)

        average_score_global = await AverageScoreGlobalModel.get_by_fields(db, id_user=user.id)

        if average_score_global:
            await average_score_global.update(db, {'rating': rating})
        else:
            average_company = AverageScoreGlobalModel(id_user=user.id, rating=rating)
            await average_company.create(db)

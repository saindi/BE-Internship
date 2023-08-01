from sqlalchemy import Column, Integer, ForeignKey, Float

from db.models import BaseModel
from analytic.models.crud import AverageScoreCompanyCrud, AverageScoreGlobalCrud


class AverageScoreCompanyModel(BaseModel, AverageScoreCompanyCrud):
    __tablename__ = "average_score_company"

    id_user = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    id_company = Column(Integer, ForeignKey("company.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Float, nullable=False)


class AverageScoreGlobalModel(BaseModel, AverageScoreGlobalCrud):
    __tablename__ = "average_score_global"

    id_user = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True)
    rating = Column(Float, nullable=False)

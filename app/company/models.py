from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from db.models import BaseModel


class CompanyModel(BaseModel):
    __tablename__ = "сompany"

    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    is_hidden = Column(Boolean, default=False, nullable=False)
    owner_id = Column(Integer,  ForeignKey('user.id'), comment='Владелец  компании')

    owner = relationship('UserModel', backref='company_owner', lazy='subquery')

    def user_can_edit(self, user_id):
        return self.owner_id == user_id

    def user_can_delete(self, user_id):
        return self.owner_id == user_id

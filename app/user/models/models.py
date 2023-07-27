from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from db.models import BaseModel
from user.models.crud import UserCrud


class UserModel(BaseModel, UserCrud):
    __tablename__ = "user"

    email = Column(String, unique=True, index=True)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    companies = relationship("CompanyModel", secondary="role", lazy="subquery")
    invitations = relationship("InvitationModel", lazy="subquery", cascade="all, delete-orphan")
    requests = relationship("RequestModel", lazy="subquery", cascade="all, delete-orphan")
    results = relationship("ResultTestModel", lazy="subquery", cascade="all, delete-orphan")

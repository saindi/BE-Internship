import enum

from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship

from company.crud import CompanyCrud
from db.models import BaseModel


class RoleEnum(enum.Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class RoleModel(BaseModel):
    __tablename__ = "role"

    id_company = Column(Integer, ForeignKey("company.id"), nullable=False)
    id_user = Column(Integer, ForeignKey("user.id"), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)


class CompanyModel(BaseModel, CompanyCrud):
    __tablename__ = "company"

    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    is_hidden = Column(Boolean, default=False, nullable=False)

    users = relationship("UserModel", secondary="role", lazy="subquery")
    roles = relationship("RoleModel", lazy="subquery", cascade="all, delete-orphan")
    invitations = relationship("InvitationModel", lazy="subquery", cascade="all, delete-orphan")
    requests = relationship("RequestModel", lazy="subquery", cascade="all, delete-orphan")
    quizzes = relationship("QuizModel", cascade="all, delete-orphan", back_populates="company", lazy="subquery")


class InvitationModel(BaseModel):
    __tablename__ = "invitation"

    id_company = Column(Integer, ForeignKey("company.id"), nullable=False)
    id_user = Column(Integer, ForeignKey("user.id"), nullable=False)


class RequestModel(BaseModel):
    __tablename__ = "request"

    id_company = Column(Integer, ForeignKey("company.id"), nullable=False)
    id_user = Column(Integer, ForeignKey("user.id"), nullable=False)

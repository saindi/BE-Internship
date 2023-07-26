import enum
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

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


class CompanyModel(BaseModel):
    __tablename__ = "company"

    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    is_hidden = Column(Boolean, default=False, nullable=False)

    users = relationship("UserModel", secondary="role", lazy="subquery")
    roles = relationship("RoleModel", lazy="subquery", cascade="all, delete-orphan")
    invitations = relationship("InvitationModel", lazy="subquery", cascade="all, delete-orphan")
    requests = relationship("RequestModel", lazy="subquery", cascade="all, delete-orphan")
    quizzes = relationship("QuizModel", cascade="all, delete-orphan", back_populates="company", lazy="subquery")

    async def create(self, db: AsyncSession, owner_id: int):
        await super().create(db)

        new_role = RoleModel(
            id_company=self.id,
            id_user=owner_id,
            role=RoleEnum.OWNER
        )

        await new_role.create(db)

    def user_can_edit(self, current_user_id: int) -> bool:
        return self.get_owner_id() == current_user_id

    def user_can_delete(self, current_user_id: int) -> bool:
        return self.get_owner_id() == current_user_id

    def user_entitled_quiz(self, current_user_id: int) -> bool:
        if self.is_owner(current_user_id) or current_user_id in self.get_id_admins():
            return True

        return False

    def is_owner(self, current_user_id: int) -> bool:
        return self.get_owner_id() == current_user_id

    def is_user_in_company(self, current_user_id: int) -> bool:
        for role in self.roles:
            if role.id_user == current_user_id:
                return True

        return False

    def get_owner_id(self) -> Optional[int]:
        for role in self.roles:
            if role.role == RoleEnum.OWNER:
                return role.id_user

        return None

    def get_owner(self):
        id_owner = self.get_owner_id()

        return [user for user in self.users if user.id == id_owner][0]

    def get_id_admins(self) -> list:
        id_admins = [role.id_user for role in self.roles if role.role == RoleEnum.ADMIN]

        return id_admins

    def get_admins(self) -> list:
        admins = [user for user in self.users if user.id in self.get_id_admins()]

        return admins

    async def add_invite_to_company(self, db, target_user):
        for user_company in self.users:
            if user_company.id == target_user.id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You are already a member of this company')

        for invite in self.invitations:
            if invite.id_user == target_user.id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='The invite has already been sent')

        for request in self.requests:
            if request.id_user == target_user.id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='There is a request from this user, accept or reject it')

        new_invite = InvitationModel(id_user=target_user.id, id_company=self.id)

        await new_invite.create(db)

        return new_invite


class InvitationModel(BaseModel):
    __tablename__ = "invitation"

    id_company = Column(Integer, ForeignKey("company.id"), nullable=False)
    id_user = Column(Integer, ForeignKey("user.id"), nullable=False)


class RequestModel(BaseModel):
    __tablename__ = "request"

    id_company = Column(Integer, ForeignKey("company.id"), nullable=False)
    id_user = Column(Integer, ForeignKey("user.id"), nullable=False)

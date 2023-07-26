from fastapi import HTTPException
from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship
from starlette import status

from company.models import RequestModel
from db.models import BaseModel
from utils.hashing import Hasher


class UserModel(BaseModel):
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

    def user_verification(self, hashed_password) -> bool:
        return Hasher.verify_password(hashed_password, self.hashed_password)

    def can_edit(self, user_id: int) -> bool:
        return self.id == user_id or self.is_superuser

    def can_delete(self, user_id: int) -> bool:
        return self.id == user_id or self.is_superuser

    async def add_request_to_company(self, db, company):
        for user_company in self.companies:
            if user_company.id == company.id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail='You are already a member of this company')

        for request in self.requests:
            if request.id_company == company.id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You already have such a request')

        for invite in self.invitations:
            if invite.id_company == company.id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail='You already have one of these invites, accept or decline it')

        new_request = RequestModel(id_user=self.id, id_company=company.id)

        await new_request.create(db)

        return new_request

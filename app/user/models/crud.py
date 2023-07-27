from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from company.models.models import RequestModel
from utils.hashing import Hasher


class UserCrud:
    def user_verification(self, hashed_password: str) -> bool:
        return Hasher.verify_password(hashed_password, self.hashed_password)

    def can_edit(self, user_id: int) -> bool:
        return self.id == user_id or self.is_superuser

    def can_delete(self, user_id: int) -> bool:
        return self.id == user_id or self.is_superuser

    async def add_request_to_company(self, db: AsyncSession, company):
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

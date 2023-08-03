from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from company.models.models import RoleModel, CompanyModel, InvitationModel, RequestModel
from utils.hashing import Hasher


class UserCrud:
    async def companies(self, db: AsyncSession):
        roles = await RoleModel.get_by_fields(db, return_single=False, id_user=self.id)

        if not roles:
            return []

        return [await CompanyModel.get_by_id(db, role.id_company) for role in roles]

    async def invitations(self, db: AsyncSession):
        invitations = await InvitationModel.get_by_fields(db, return_single=False, id_user=self.id)

        return invitations if invitations else []

    async def requests(self, db: AsyncSession):
        requests = await RequestModel.get_by_fields(db, return_single=False, id_user=self.id)

        return requests if requests else []

    def user_verification(self, hashed_password: str) -> bool:
        return Hasher.verify_password(hashed_password, self.hashed_password)

    def can_edit(self, user_id: int) -> bool:
        return self.id == user_id

    def can_delete(self, user_id: int) -> bool:
        return self.id == user_id

    def can_read(self, user_id: int) -> bool:
        return self.id == user_id

    async def add_request_to_company(self, db: AsyncSession, company):
        for user_company in await self.companies(db):
            if user_company.id == company.id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail='You are already a member of this company')

        for request in await self.requests(db):
            if request.id_company == company.id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='You already have such a request')

        for invite in await self.invitations(db):
            if invite.id_company == company.id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail='You already have one of these invites, accept or decline it')

        new_request = RequestModel(id_user=self.id, id_company=company.id)

        await new_request.create(db)

        return new_request


class NotificationCrud:
    @staticmethod
    async def notification_for_users(db: AsyncSession, users, msg: str):
        from user.models.models import NotificationModel

        [(await NotificationModel(id_user=user.id, text=msg).create(db)) for user in users]

    @staticmethod
    async def delete_read(db: AsyncSession, user_id: int):
        from user.models.models import NotificationModel, StatusEnum

        notifications = await NotificationModel.get_by_fields(
            db,
            return_single=False,
            id_user=user_id,
            status=StatusEnum.READ.value
        )

        if notifications:
            [(await notification.delete(db)) for notification in notifications]

            return {'detail': f'Success delete notifications'}
        else:
            return {'detail': f'No such read notifications'}

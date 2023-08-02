from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


class CompanyCrud:
    async def create_with_owner(self, db: AsyncSession, owner_id: int):
        from company.models.models import RoleModel, RoleEnum

        await self.create(db)

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

    def is_user_manager(self, current_user_id: int) -> bool:
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
        from company.models.models import RoleEnum

        for role in self.roles:
            if role.role == RoleEnum.OWNER:
                return role.id_user

        return None

    def get_owner(self):
        id_owner = self.get_owner_id()

        return [user for user in self.users if user.id == id_owner][0]

    def get_id_admins(self) -> list:
        from company.models.models import RoleEnum

        id_admins = [role.id_user for role in self.roles if role.role == RoleEnum.ADMIN]

        return id_admins

    def get_admins(self) -> list:
        admins = [user for user in self.users if user.id in self.get_id_admins()]

        return admins

    async def add_invite_to_company(self, db: AsyncSession, target_user):
        from company.models.models import InvitationModel

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

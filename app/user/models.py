from sqlalchemy import Boolean, Column, String

from db.models import BaseModel
from utils.hashing import Hasher


class UserModel(BaseModel):
    __tablename__ = "user"

    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    def user_verification(self, hashed_password):
        return Hasher.verify_password(hashed_password, self.hashed_password)

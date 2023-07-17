from sqlalchemy import Boolean, Column, String

from db.models import BaseModel


class UserModel(BaseModel):
    __tablename__ = "user"

    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

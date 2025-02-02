import enum

from sqlalchemy import Boolean, Column, String, Integer, ForeignKey, Enum

from db.models import BaseModel
from user.models.crud import UserCrud, NotificationCrud


class FileNameEnum(enum.Enum):
    ALL_RESULTS_USER = 'all_results_user.csv'
    TEST_RESULT = 'test_result.csv'


class UserModel(BaseModel, UserCrud):
    __tablename__ = "user"

    email = Column(String, unique=True, index=True)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)


class StatusEnum(enum.Enum):
    NEW = "NEW"
    READ = "READ"


class NotificationModel(BaseModel, NotificationCrud):
    __tablename__ = "notification"

    id_user = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    text = Column(String, nullable=False)
    status = Column(Enum(StatusEnum), nullable=False, default=StatusEnum.NEW.value)

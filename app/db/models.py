from datetime import datetime

from sqlalchemy import Column, Integer, DateTime

from db.crud import BaseCRUD


class BaseModel(BaseCRUD):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

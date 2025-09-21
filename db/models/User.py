from sqlalchemy import Column, DateTime, Integer, String, Boolean
from sqlalchemy.sql import func
from db.Base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    telegram_id = Column(String, index=True, unique=True, nullable=False)
    chat_id = Column(String, nullable=True)
    user_name = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    language_bot = Column(String)
    is_bot = Column(Boolean, default=False)
    search_keywords = Column(String)
    is_active = Column(Boolean, default=True)
    status = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    last_active = Column(DateTime, default=func.now(), nullable=False)
    last_recent_job_id = Column(Integer, default=0, nullable=False)

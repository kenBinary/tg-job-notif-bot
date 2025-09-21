from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.sql import func
from db.Base import Base


class LastRecentJob(Base):
    __tablename__ = "LastRecentJob"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    last_recent_job_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=True
    )

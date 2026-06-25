from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func

from src.api.db.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    task_type = Column(String, nullable=False)
    priority = Column(Integer, default=5)
    status = Column(String, default="PENDING")
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
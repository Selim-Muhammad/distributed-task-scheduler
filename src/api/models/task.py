from sqlalchemy import Column, String, Integer
from src.api.db.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    task_type = Column(String, nullable=False)
    priority = Column(Integer, default=5)
    status = Column(String, default="PENDING")
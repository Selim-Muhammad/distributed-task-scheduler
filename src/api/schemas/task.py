from pydantic import BaseModel


class TaskCreate(BaseModel):
    task_type: str
    priority: int = 5


class TaskResponse(BaseModel):
    id: str
    task_type: str
    priority: int
    status: str
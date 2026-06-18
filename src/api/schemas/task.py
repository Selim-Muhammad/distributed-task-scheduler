from pydantic import BaseModel


class TaskCreate(BaseModel):
    task_type: str
    priority: int = 5
    max_retries: int = 3


class TaskResponse(BaseModel):
    id: str
    task_type: str
    priority: int
    status: str
    retry_count: int
    max_retries: int
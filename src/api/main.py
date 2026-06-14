import uuid

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.db.database import Base, engine, SessionLocal
from src.api.models.task import Task
from src.api.schemas.task import TaskCreate, TaskResponse

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "service": "distributed-task-scheduler-api"
    }


@app.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = Task(
        id=str(uuid.uuid4()),
        task_type=task.task_type,
        priority=task.priority,
        status="PENDING"
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task
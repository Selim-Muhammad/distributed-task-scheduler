import uuid

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.db.database import Base, engine, SessionLocal
from src.api.models.task import Task
from src.api.schemas.task import TaskCreate, TaskResponse
from src.api.queue.redis_client import redis_client

# Create database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Health check endpoint
@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "service": "distributed-task-scheduler-api"
    }


# Create a new task
@app.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = Task(
        id=str(uuid.uuid4()),
        task_type=task.task_type,
        priority=task.priority,
        status="PENDING"
    )

    # Save task to PostgreSQL
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # Push task into Redis priority queue
    redis_client.zadd(
        "task_queue",
        {new_task.id: new_task.priority}
    )

    return new_task


# Get a task by ID
@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task
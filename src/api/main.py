import uuid

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.api.db.database import Base, engine, SessionLocal
from src.api.models.task import Task
from src.api.schemas.task import TaskCreate, TaskResponse
from src.api.queue.redis_client import redis_client


# Create database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        status="PENDING",
        retry_count=0,
        max_retries=task.max_retries
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


@app.get("/workers")
def get_workers():
    worker_keys = redis_client.keys("worker:*")
    workers = []

    for key in worker_keys:
        worker = redis_client.hgetall(key)
        workers.append(worker)

    return {
        "workers": workers,
        "count": len(workers)
    }


@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    queue_depth = redis_client.zcard("task_queue")

    alive_workers = len(
        redis_client.keys("worker:*")
    )

    completed_tasks = (
        db.query(Task)
        .filter(Task.status == "COMPLETED")
        .count()
    )

    pending_tasks = (
        db.query(Task)
        .filter(Task.status == "PENDING")
        .count()
    )

    running_tasks = (
        db.query(Task)
        .filter(Task.status == "RUNNING")
        .count()
    )

    dead_tasks = (
        db.query(Task)
        .filter(Task.status == "DEAD")
        .count()
    )

    return {
        "queue_depth": queue_depth,
        "alive_workers": alive_workers,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "running_tasks": running_tasks,
        "dead_tasks": dead_tasks
    }
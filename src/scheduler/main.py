import time

from src.api.db.database import SessionLocal
from src.api.models.task import Task
from src.api.queue.redis_client import redis_client


def dispatch_task(task_id: str, priority: float):
    db = SessionLocal()

    try:
        task = db.query(Task).filter(Task.id == task_id).first()

        if task is None:
            print(f"Task {task_id} not found in database")
            return

        task.status = "RUNNING"
        db.commit()

        print(f"Dispatching task {task_id} (priority={priority})")

    finally:
        db.close()


def run_scheduler():
    print("Scheduler started...")

    try:
        while True:
            task = redis_client.zpopmax("task_queue")

            if task:
                task_id, priority = task[0]
                dispatch_task(task_id, priority)

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nScheduler stopped gracefully.")


if __name__ == "__main__":
    run_scheduler()
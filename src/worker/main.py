import time

from src.api.db.database import SessionLocal
from src.api.models.task import Task
from src.api.queue.redis_client import redis_client


def execute_task(task: Task):
    print(f"Worker executing task {task.id} ({task.task_type})")

    time.sleep(2)

    print(f"Worker completed task {task.id}")


def release_lease(task_id: str):
    redis_client.delete(f"lease:{task_id}")


def run_worker():
    print("Worker started...")

    try:
        while True:
            db = SessionLocal()

            task = (
                db.query(Task)
                .filter(Task.status == "RUNNING")
                .first()
            )

            if task:
                execute_task(task)

                task.status = "COMPLETED"
                db.commit()

                release_lease(task.id)

            db.close()

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nWorker stopped gracefully.")


if __name__ == "__main__":
    run_worker()
import time

from src.api.db.database import SessionLocal
from src.api.models.task import Task


def execute_task(task: Task):
    print(f"Worker executing task {task.id} ({task.task_type})")

    time.sleep(2)

    print(f"Worker completed task {task.id}")


def run_worker():
    print("Worker started...")

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

        db.close()

        time.sleep(1)


if __name__ == "__main__":
    run_worker()
import random
import time


from src.api.db.database import SessionLocal
from src.api.models.task import Task
from src.api.queue.redis_client import redis_client


def execute_task(task: Task):
    print(f"Worker executing task {task.id} ({task.task_type})")

    time.sleep(2)

    if random.random() < 0.3:
       raise Exception("Simulated task failure")
    
    print(f"Worker completed task {task.id}")

    


def release_lease(task_id: str):
    redis_client.delete(f"lease:{task_id}")


def requeue_task(task: Task):
    redis_client.zadd(
        "task_queue",
        {task.id: task.priority}
    )


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
                try:
                    execute_task(task)

                    task.status = "COMPLETED"
                    db.commit()

                    release_lease(task.id)

                except Exception as error:
                    task.retry_count += 1

                    if task.retry_count <= task.max_retries:
                        task.status = "PENDING"
                        db.commit()

                        release_lease(task.id)
                        requeue_task(task)

                        print(
                            f"Task {task.id} failed. "
                            f"Retrying ({task.retry_count}/{task.max_retries})"
                        )

                    else:
                        task.status = "DEAD"
                        db.commit()

                        release_lease(task.id)

                        print(
                            f"Task {task.id} moved to DEAD. "
                            f"Reason: {error}"
                        )

            db.close()

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nWorker stopped gracefully.")


if __name__ == "__main__":
    run_worker()
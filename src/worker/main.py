import random
import socket
import time
import uuid

from src.api.db.database import SessionLocal
from src.api.models.task import Task
from src.api.queue.redis_client import redis_client


WORKER_ID = f"{socket.gethostname()}-{uuid.uuid4()}"
HEARTBEAT_TTL_SECONDS = 10


def register_worker():
    redis_client.hset(
        f"worker:{WORKER_ID}",
        mapping={
            "worker_id": WORKER_ID,
            "hostname": socket.gethostname(),
            "status": "ALIVE",
            "last_seen": time.time()
        }
    )

    redis_client.expire(f"worker:{WORKER_ID}", HEARTBEAT_TTL_SECONDS)

    print(f"Worker registered: {WORKER_ID}")


def send_heartbeat():
    redis_client.hset(
        f"worker:{WORKER_ID}",
        mapping={
            "status": "ALIVE",
            "last_seen": time.time()
        }
    )

    redis_client.expire(f"worker:{WORKER_ID}", HEARTBEAT_TTL_SECONDS)


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


def get_next_assigned_task_id():
    task_id = redis_client.lpop(f"worker_queue:{WORKER_ID}")
    return task_id


def process_task(task_id: str):
    db = SessionLocal()

    try:
        task = db.query(Task).filter(Task.id == task_id).first()

        if task is None:
            print(f"Task {task_id} not found in database")
            release_lease(task_id)
            return

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

    finally:
        db.close()


def run_worker():
    print("Worker started...")
    register_worker()

    try:
        while True:
            send_heartbeat()

            task_id = get_next_assigned_task_id()

            if task_id:
                process_task(task_id)

            time.sleep(0.5)

    except KeyboardInterrupt:
        redis_client.delete(f"worker:{WORKER_ID}")
        redis_client.delete(f"worker_queue:{WORKER_ID}")
        print("\nWorker stopped gracefully.")


if __name__ == "__main__":
    run_worker()
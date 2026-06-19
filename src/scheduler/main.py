import time

from src.api.db.database import SessionLocal
from src.api.models.task import Task
from src.api.queue.redis_client import redis_client


LEASE_TTL_SECONDS = 30


def get_alive_workers():
    worker_keys = redis_client.keys("worker:*")
    alive_workers = []

    for key in worker_keys:
        worker = redis_client.hgetall(key)

        if worker.get("status") == "ALIVE":
            alive_workers.append(worker)

    return alive_workers


def acquire_lease(task_id: str) -> bool:
    return redis_client.set(
        name=f"lease:{task_id}",
        value="LOCKED",
        nx=True,
        ex=LEASE_TTL_SECONDS
    )


def dispatch_task(task_id: str, priority: float):
    alive_workers = get_alive_workers()

    if not alive_workers:
        redis_client.zadd("task_queue", {task_id: priority})
        print("No alive workers available. Task returned to queue.")
        return

    lease_acquired = acquire_lease(task_id)

    if not lease_acquired:
        print(f"Could not acquire lease for task {task_id}")
        return

    selected_worker = alive_workers[0]

    db = SessionLocal()

    try:
        task = db.query(Task).filter(Task.id == task_id).first()

        if task is None:
            print(f"Task {task_id} not found in database")
            return

        task.status = "RUNNING"
        db.commit()

        print(
            f"Dispatching task {task_id} "
            f"(priority={priority}) "
            f"to worker {selected_worker.get('worker_id')}"
        )

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
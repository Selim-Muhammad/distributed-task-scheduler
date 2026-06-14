import time

from src.api.queue.redis_client import redis_client


print("Scheduler started...")

while True:
    task = redis_client.zpopmax("task_queue")

    if task:
        task_id, priority = task[0]

        print(
            f"Dispatching task {task_id} "
            f"(priority={priority})"
        )

    time.sleep(1)
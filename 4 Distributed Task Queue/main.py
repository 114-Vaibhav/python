import redis
import json
import time
import uuid
from multiprocessing import Process


r = redis.Redis(host='localhost', port=6379, db=0)

class Task:
    def __init__(self, func_name, args=None, kwargs=None):
        self.id = uuid.uuid4().hex[:8]
        self.func_name = func_name
        self.args = args or []
        self.kwargs = kwargs or {}
        self.status = "PENDING"
        self.retries = 0
        self.max_retries = 3


FUNCTIONS = {}

def register(func):
    FUNCTIONS[func.__name__] = func
    return func


def enqueue(task):
    r.lpush("task_queue", json.dumps(task.__dict__))
    print(f"Task queued: {task.id} ")


def handle_retry(task, error):
    task["retries"] += 1

    if task["retries"] > task["max_retries"]:
        r.lpush("dead_letter_queue", json.dumps(task))
        print(f"[DLQ] Task {task['id']} failed permanently")
        return

    delay = 2 ** task["retries"]
    print(f"[RETRY] Task {task['id']} retry {task['retries']} in {delay}s")

    time.sleep(delay)
    r.lpush("task_queue", json.dumps(task))


def worker(worker_id):
    print(f"[WORKER-{worker_id}] Started")

    while True:
        _, task_data = r.brpop("task_queue")
        task = json.loads(task_data)

        func = FUNCTIONS[task["func_name"]]

        try:
            print(f"[WORKER-{worker_id}] Running {task['id']}: ")

            start = time.time()
            result = func(*task["args"], **task["kwargs"])
            duration = time.time() - start

            r.set(f"results:{task['id']}", json.dumps({
                "status": "SUCCESS",
                "result": str(result),
                "duration": duration,
                "retries": task["retries"]
            }))

            print(f"[SUCCESS] {task['id']} in {duration:.2f}s")

        except Exception as e:
            print(f"[ERROR] {task['id']} → {e}")
            handle_retry(task, str(e))


@register
def send_email(to):
    import random
    if random.random() < 0.8:
        raise Exception("SMTP Error")
    return f"Email sent to {to}"

@register
def generate_thumbnail(image_id, size):
    time.sleep(1)
    return f"/thumbs/{image_id}_{size}.jpg"


def dashboard():
    print("\n=== DASHBOARD ===")
    for key in r.keys("results:*"):
        data = json.loads(r.get(key))
        print(key.decode(), data)



if __name__ == "__main__":
    # Start workers
    for i in range(3):
        Process(target=worker, args=(i+1,)).start()

    time.sleep(1)

    # Produce tasks
    enqueue(Task("generate_thumbnail", kwargs={"image_id": 1504, "size": (256,256)}))
    enqueue(Task("generate_thumbnail", kwargs={"image_id": 2611, "size": (256,256)}))
    enqueue(Task("send_email", kwargs={"to": "vg@presidio.com"}))
    enqueue(Task("send_email", kwargs={"to": "vgp@prd.com"}))

    time.sleep(10)
    # dashboard()
    # r.flushdb()
    dashboard()
    

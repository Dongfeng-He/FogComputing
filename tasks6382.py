from celery import Celery
import time
import redis
from defer import DeferrableTask
from message import result_message

'''
def update_queuing_time(func):
    alpha = 0.1
    def wrapper(*args):
        start_time = time.time()
        func(*args)
        end_time = time.time()
        processing_time = end_time - start_time
        queuing_time = float(r.get('queuing_time'))
        new_queuing_time = queuing_time * (1 - alpha) + processing_time * alpha
        r.set('queuing_time', new_queuing_time)
    return wrapper
'''

def update_queuing_time(start_time, task_type):
    end_time = time.time()
    new_queuing_time = end_time - start_time
    print(new_queuing_time)
    r.set(task_type, new_queuing_time)

def setTaskTime():
    for task_name in all_task_name:
        r.set(task_name, 0)

def getTaskTime():
    all_task_time = {}
    for task_name in all_task_name:
        all_task_time[task_name] = float(r.get(task_name))

    return all_task_time

r = redis.Redis(host='localhost', port=6382, decode_responses=True)

broker = 'redis://127.0.0.1:6382/5'
backend = 'redis://127.0.0.1:6382/6'

app = Celery('tasks', broker = broker, backend = backend)

all_task_name = ["add"]



@DeferrableTask
@app.task
def add(content, task_id):
    result = result_message
    result["task_id"] = task_id
    start_time = time.time()
    result["content"] = pow(3523523523,34232) % 4
    update_queuing_time(start_time, "add")

    return result











from celery import Celery
import time
import redis
from defer import DeferrableTask


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
    r.set(task_type, new_queuing_time)

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

broker = 'redis://127.0.0.1:6379/5'
backend = 'redis://127.0.0.1:6379/6'

app = Celery('tasks', broker = broker, backend = backend)


@DeferrableTask
@app.task
def add(x):
    start_time = time.time()
    pow(3523523523,34232)
    update_queuing_time(start_time, "add")
    return "add result"











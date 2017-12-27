from celery import Celery
import time
import redis
import json
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

def update_queuing_time(start_time):
    alpha = 0.1
    end_time = time.time()
    processing_time = end_time - start_time
    queuing_time = float(r.get('queuing_time'))
    new_queuing_time = queuing_time * (1 - alpha) + processing_time * alpha
    r.set('queuing_time', new_queuing_time)

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

broker = 'redis://127.0.0.1:6379/5'
backend = 'redis://127.0.0.1:6379/6'

app = Celery('tasks', broker = broker, backend = backend)


@DeferrableTask
@app.task
def add(x, y):
    start_time = time.time()
    time.sleep(10)
    update_queuing_time(start_time)
    result = x + y
    return json.dumps(result)

@app.task
def minus(x, y):
    return x - y









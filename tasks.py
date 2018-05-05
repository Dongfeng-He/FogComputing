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

def resetTaskTime():
    for task_name in all_task_name:
        r.set(task_name, 0)

def resetQueueState():
    r.set('light_task_num', 0)
    r.set('medium_task_num', 0)
    r.set('heavy_task_num', 0)

def getAllTaskTime():
    all_task_time = {}
    for task_name in all_task_name:
        all_task_time[task_name] = float(r.get(task_name))
    return all_task_time

def taskInQueue():
    light_task_num = r.get('light_task_num')
    medium_task_num = r.get('medium_task_num')
    heavy_task_num = r.get('heavy_task_num')
    if light_task_num == None:
        light_task_num = 0;
    else:
        light_task_num = int(light_task_num)
    if medium_task_num == None:
        medium_task_num = 0;
    else:
        medium_task_num = int(medium_task_num)
    if heavy_task_num == None:
        heavy_task_num = 0;
    else:
        heavy_task_num = int(heavy_task_num)
    sum = light_task_num + medium_task_num + heavy_task_num
    return sum, light_task_num, medium_task_num, heavy_task_num


r = redis.Redis(host='localhost', port=6379, decode_responses=True)

broker = 'redis://127.0.0.1:6379/5'
backend = 'redis://127.0.0.1:6379/6'

app = Celery('tasks', broker = broker, backend = backend)

all_task_name = ["add"]



@DeferrableTask
@app.task
def add(content, task_id):
    light_task_num = r.get('light_task_num')
    print(light_task_num)
    if light_task_num == None:
        r.set('light_task_num', 1)
    else:
        r.set('light_task_num', int(light_task_num) + 1)
    result = result_message
    result["task_id"] = task_id
    start_time = time.time()
    result["content"] = pow(3523523523,34232) % 4
    update_queuing_time(start_time, "add")
    light_task_num = r.get('light_task_num')
    r.set('light_task_num', int(light_task_num) - 1)

    return result











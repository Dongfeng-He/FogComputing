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
    r.set('last_light_time', 0)
    r.set('2nd_last_light_time', 0)
    r.set('estimated_light_time', 0)
    r.set('last_medium_time', 0)
    r.set('2nd_last_medium_time', 0)
    r.set('estimated_medium_time', 0)
    r.set('last_heavy_time', 0)
    r.set('2nd_last_heavy_time', 0)
    r.set('estimated_heavy_time', 0)

def resetQueueState():
    r.set('light_task_num', 0)
    r.set('medium_task_num', 0)
    r.set('heavy_task_num', 0)

def getAllTaskTime():
    all_task_time = {}
    all_task_time['estimated_light_time'] = float(r.get('estimated_light_time'))
    all_task_time['estimated_medium_time'] = float(r.get('estimated_medium_time'))
    all_task_time['estimated_heavy_time'] = float(r.get('estimated_heavy_time'))
    return all_task_time

def taskInQueue():
    task_num_in_queue = {}
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
    total_task_num = light_task_num + medium_task_num + heavy_task_num
    task_num_in_queue['light_task_num'] = light_task_num
    task_num_in_queue['medium_task_num'] = medium_task_num
    task_num_in_queue['heavy_task_num'] = heavy_task_num
    task_num_in_queue['total_task_num'] = total_task_num
    return task_num_in_queue

def getWaitingTime():
    task_num = taskInQueue()
    light_task_num = task_num['light_task_num']
    medium_task_num = task_num['medium_task_num']
    heavy_task_num = task_num['heavy_task_num']
    task_time = getAllTaskTime()
    light_task_time = task_time['estimated_light_time']
    medium_task_time = task_time['estimated_medium_time']
    heavy_task_time = task_time['estimated_heavy_time']
    waiting_time = light_task_num * light_task_time + medium_task_num * medium_task_time + heavy_task_num * heavy_task_time
    return waiting_time

def getExecutionTime(task_type):
    if task_type == 'light':
        execution_time = float(r.get('estimated_light_time'))
    elif task_type == 'medium':
        execution_time = float(r.get('estimated_medium_time'))
    elif task_type == 'heavy':
        execution_time = float(r.get('estimated_heavy_time'))
    else:
        execution_time = 100000
    return execution_time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

broker = 'redis://127.0.0.1:6379/5'
backend = 'redis://127.0.0.1:6379/6'

app = Celery('tasks', broker = broker, backend = backend)

#all_task_name = ["light"]



@DeferrableTask
@app.task
def light(task_message, enqueue_time):
    start_time = time.time()
    queuing_time = start_time - enqueue_time
    print("Number of light-weight task in queue: %s" % r.get('light_task_num'))
    print('Estimated queuing time: %f' % task_message['estimated_queuing_time'])
    print('Actual queuing time: %f' % queuing_time)
    task_content = task_message['content']
    result = result_message
    result["task_id"] = task_message['task_id']
    result["content"] = pow(3523523523,3423) % 4
    light_task_num = r.get('light_task_num')
    update_queuing_time(enqueue_time, 'light')
    execution_time = time.time() - start_time
    previous_last_time = float(r.get('last_light_time'))
    previous_2nd_last_time = float(r.get('2nd_last_light_time'))
    if previous_2nd_last_time != 0:
        estimated_light_time = execution_time * 0.5 + previous_last_time * 0.3 + previous_2nd_last_time * 0.2
    elif previous_last_time != 0:
        estimated_light_time = execution_time * 0.7 + previous_last_time * 0.3
    else:
        estimated_light_time = execution_time
    r.set('last_light_time', execution_time)
    r.set('2nd_last_light_time', previous_last_time)
    r.set('estimated_light_time', estimated_light_time)
    r.set('light_task_num', int(light_task_num) - 1)
    print('Estimated execution time: %f' %  task_message['estimated_execution_time'])
    print('Actual execution time: %f' % execution_time)
    return result

@DeferrableTask
@app.task
def medium(task_message, enqueue_time):
    start_time = time.time()
    queuing_time = start_time - enqueue_time
    print("Number of medium-weight task in queue: %s" % r.get('medium_task_num'))
    print('Estimated queuing time: %f' % task_message['estimated_queuing_time'])
    print('Actual queuing time: %f' % queuing_time)
    task_content = task_message['content']
    result = result_message
    result["task_id"] = task_message['task_id']
    result["content"] = pow(3523523523,342323) % 4
    medium_task_num = r.get('medium_task_num')
    execution_time = time.time() - start_time
    update_queuing_time(enqueue_time, 'medium')
    previous_last_time = float(r.get('last_medium_time'))
    previous_2nd_last_time = float(r.get('2nd_last_medium_time'))
    if previous_2nd_last_time != 0:
        estimated_medium_time = execution_time * 0.5 + previous_last_time * 0.3 + previous_2nd_last_time * 0.2
    elif previous_last_time != 0:
        estimated_medium_time = execution_time * 0.7 + previous_last_time * 0.3
    else:
        estimated_medium_time = execution_time
    r.set('last_medium_time', execution_time)
    r.set('2nd_last_medium_time', previous_last_time)
    r.set('estimated_medium_time', estimated_medium_time)
    r.set('medium_task_num', int(medium_task_num) - 1)
    print('Estimated execution time: %f' % task_message['estimated_execution_time'])
    print('Actual execution time: %f' % execution_time)
    return result

@DeferrableTask
@app.task
def heavy(task_message, enqueue_time):
    start_time = time.time()
    queuing_time = start_time - enqueue_time
    print("Number of heavy-weight task in queue: %s" % r.get('heavy_task_num'))
    print('Estimated queuing time: %f' % task_message['estimated_queuing_time'])
    print('Actual queuing time: %f' % queuing_time)
    task_content = task_message['content']
    result = result_message
    result["task_id"] = task_message['task_id']
    result["content"] = pow(3523523523,442323) % 4
    heavy_task_num = r.get('heavy_task_num')
    execution_time = time.time() - start_time
    update_queuing_time(enqueue_time, 'heavy')
    previous_last_time = float(r.get('last_heavy_time'))
    previous_2nd_last_time = float(r.get('2nd_last_heavy_time'))
    if previous_2nd_last_time != 0:
        estimated_heavy_time = execution_time * 0.5 + previous_last_time * 0.3 + previous_2nd_last_time * 0.2
    elif previous_last_time != 0:
        estimated_heavy_time = execution_time * 0.7 + previous_last_time * 0.3
    else:
        estimated_heavy_time = execution_time
    r.set('last_heavy_time', execution_time)
    r.set('2nd_last_heavy_time', previous_last_time)
    r.set('estimated_heavy_time', estimated_heavy_time)
    r.set('heavy_task_num', int(heavy_task_num) - 1)
    print('Estimated execution time: %f' % task_message['estimated_execution_time'])
    print('Actual execution time: %f' % execution_time)
    return result










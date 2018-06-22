from celery import Celery
import time
import redis
from defer import DeferrableTask
from message import result_message

# Calculate the queuing time for for a take type and store it in Redis
def update_queuing_time(start_time, task_type):
    end_time = time.time()
    new_queuing_time = end_time - start_time
    r.set(task_type, new_queuing_time)

# Set the estimated execution time of all task types to 0 in Redis
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

# Set the number of tasks of all task types to 0 in Redis
def resetQueueState():
    r.set('light_task_num', 0)
    r.set('medium_task_num', 0)
    r.set('heavy_task_num', 0)

# Get the estimated execution time of all task types
def getAllTaskTime():
    all_task_time = {}
    all_task_time['estimated_light_time'] = float(r.get('estimated_light_time'))
    all_task_time['estimated_medium_time'] = float(r.get('estimated_medium_time'))
    all_task_time['estimated_heavy_time'] = float(r.get('estimated_heavy_time'))
    return all_task_time

# Get the number of tasks of all task types in the task queue
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

# Calculate the estimated waiting for the incoming task based on the queue status
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

# Get the estimated execution time of all task types
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

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
broker = 'redis://127.0.0.1:6379/5'
backend = 'redis://127.0.0.1:6379/6'

# Connect to Celery
app = Celery('tasks', broker = broker, backend = backend)

# This is a template for lightweight task
# Customize your own task below "Task Start" comment
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
    # -------- Task Start --------
    # e.g This is a lightweight power calculation
    result["content"] = pow(3523523523,3423) % 4
    # -------- Task End --------
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
    result['time_requirement'] = task_message['time_requirement']
    result['sending_time'] = task_message['sending_time']
    result['distribution_time'] = task_message['distribution_time']
    result['execution_time'] = execution_time
    result['task_type'] = 'light'
    result['offload_times'] = task_message['offload_times']
    result['process_by'] = task_message['process_by']
    return result

# This is a template for middleweight task
# Customize your own task below "Task Start" comment
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
    # -------- Task Start --------
    # e.g This is a middleweight power calculation
    result["content"] = pow(3523523523,342323) % 4
    # -------- Task End --------
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
    result['time_requirement'] = task_message['time_requirement']
    result['sending_time'] = task_message['sending_time']
    result['distribution_time'] = task_message['distribution_time']
    result['execution_time'] = execution_time
    result['task_type'] = 'medium'
    result['offload_times'] = task_message['offload_times']
    result['process_by'] = task_message['process_by']
    return result

# This is a template for heavyweight task
# Customize your own task below "Task Start" comment
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
    # -------- Task Start --------
    # e.g This is a heavyweight power calculation
    result["content"] = pow(3523523523,442323) % 4
    # -------- Task End --------
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
    result['time_requirement'] = task_message['time_requirement']
    result['sending_time'] = task_message['sending_time']
    result['distribution_time'] = task_message['distribution_time']
    result['execution_time'] = execution_time
    result['task_type'] = 'heavy'
    result['offload_times'] = task_message['offload_times']
    result['process_by'] = task_message['process_by']
    return result










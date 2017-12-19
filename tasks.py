from celery import Celery
import time
import redis   # 导入redis模块，通过python操作redis 也可以直接在redis主机的服务端操作缓存数据库

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

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

broker = 'redis://127.0.0.1:6379/5'
backend = 'redis://127.0.0.1:6379/6'

app = Celery('tasks', broker = broker, backend = backend)



@app.task
@update_queuing_time
def add(x, y):
      # host是redis主机，需要redis服务端和客户端都启动 redis默认端口是6379
    r.set('name',111)
    return 2

@app.task
def minus(x, y):
    return x - y







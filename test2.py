from communication import *
import time
import redis

broadcaster = UDPBroadcaster()
broadcaster.send("1")

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
r.set('queuing_time', 0)
def update_queuing_time(func):
    alpha = 0.1
    def wrapper(*args):
        start_time = time.time()
        func(*args)
        end_time = time.time()
        processing_time = end_time - start_time
        queuing_time = int(r.get('queuing_time'))
        new_queuing_time = queuing_time * (1 - alpha) + processing_time * alpha
        r.set('queuing_time', new_queuing_time)
    return wrapper


@update_queuing_time
def add(x, y):
      # host是redis主机，需要redis服务端和客户端都启动 redis默认端口是6379
    r.set('name',111)
    return 2



add(1,1)
time.sleep(0.01)
print(r.get('queuing_time'))
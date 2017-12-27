from tasks import add, minus
import time

import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
r.set('name', 'junxi')
print(r['name'])
print(r.get('name'))
r.set('queuing_time', 0)


async_result = add.delay(2, 1)
print(add.delay(2, 1).get())
print(r.get('name'))
async_result = minus.delay(1, 1)
print(async_result.get())

time.sleep(0.001)
print(r.get('queuing_time'))





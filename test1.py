from tasks import add
import time

import redis

r = redis.Redis(host='localhost', port=6380, decode_responses=True)
#r.set("add", 1)
print(r.get("add"))





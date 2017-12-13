#!/usr/bin/python3

import redq
import time

r = redq.RedisQueue(ttl=1)
x = r.get()
print(r.tasks_pending())
r.task_done(x.taskid)
y = r.get()
r.task_done(y.taskid)
print(r.tasks_pending())

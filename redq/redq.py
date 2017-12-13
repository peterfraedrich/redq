#!/usr/bin/env python3

import redis
import time
import uuid
import asyncio
import collections

class RedisQueue:
    '''
    Implements a redis based queue using redis keys instead of pubsub.
    '''

    ### PRIVATE ###
    def _decode(self, bstr):
        '''
        Converts a binary string (ASCII) to unicode
        :param: bstr :binary: -- binary string to convert
        '''
        if self.decode and bstr is not None:
            return bstr.decode('ascii')
        else:
            return bstr

    def _task_pending(self, task):
        '''
        :param: task :any: -- a task to set to pending
        Sets the task as 'pending' by moving it to a
        'pending' queue.
        '''

    def _cleanup(self):
        '''
        Goes through pending keys and cleans up if their delta is > self.ttl
        '''
        if self.safemode and self.garbage_collect:
            last_gc = self.r.get(self.GC)
            if last_gc == None or (time.time() - float(last_gc.decode('ascii'))) > 10:
                pending = []
                for task in self.r.scan_iter(self.PENDING + '*'):
                    pending.append(task.decode('ascii').replace('redq:pending:', ''))
                for taskid in pending:
                    task = self.r.hgetall(self.PENDING + taskid)
                    delta = int((time.time() - float(task[b'timestamp'])) / 60)
                    if delta > self.ttl:
                        self.r.lpush(self.Q, task[b'task'].decode('ascii'))
                        self.r.delete(self.PENDING + taskid)
                self.r.set(self.GC, time.time())
        return

    ### PUBLIC ###

    def __init__(self, redis_host='localhost', redis_port=6379, redis_auth=None, redis_db=0, qname='redq', ttl=15, safemode=True, gc=True, decode_strings=True):
        '''
        Setup the queue and set the queue name (optional).
        :param: redis_host :str: -- the redis host to connect to (defaults to localhost)
        :param: redis_port :int: -- redis port to connect on (defaults to 6379)
        :param: redis_auth :str: -- the redis auth string to use (defaults to None [no auth])
        :param: redis_db :int: -- the db index to use (defaults to 0)
        :param: safemode :bool: -- resubmit tasks to queue if not done after <qtimeout>
        :param: gc :bool: -- cleanup tasks after re-submitted to queue
        :param: ttl :int: --  time to resubmit tasks to queue
        :param: decode_strings :bool: -- Decode strings to ASCII
        '''
        # set up some boilerplate stuff here
        self.Task = collections.namedtuple('Task', ['task', 'taskid'])
        self.ttl = int(ttl)
        self.garbage_collect = gc
        self.decode = decode_strings
        self.qname = qname
        self.Q = '{}:q'.format(qname)
        self.GC = '{}:gc'.format(qname)
        self.safemode = safemode
        self.PENDING = '{}:pending:'.format(qname)
        # initiate our redis connection
        self.r = redis.StrictRedis(host=str(redis_host), port=int(redis_port), db=int(redis_db), password=redis_auth)
        self.r.set('{}:queue_init'.format(qname), time.time())
        # set up async loop so we can run background tasks
        self.loop = asyncio.get_event_loop()
        self._cleanup()
        return


    def put(self, item):
        '''
        Pushes an item onto the queue
        :param: item :any: -- the item to push to the queue
        '''
        self.r.rpush(self.Q, item)
        self.loop.call_soon(self._cleanup)
        return


    def put_first(self, item):
        '''
        :param: item :any: -- the item to push to the queue
        Pushes an item onto the front of the queue
        '''
        self.r.lpush(self.Q, item)
        self.loop.call_soon(self._cleanup)
        return


    def get(self, blocking=False):
        '''
        :param: blocking :bool: -- Block until a task is available
        Gets a task from the queue
        Returns a Task object tuple (task, taskid)
        '''
        taskid = str(uuid.uuid4()).replace('-', '')
        if not blocking:
            item = self.r.lpop(self.Q)
        else:
            item = self.r.blpop(self.Q)
        if self.safemode and item is not None:
            task = {
                'task' : item,
                'timestamp' : time.time(),
                'taskid' : taskid
            }
            self.r.hmset(self.PENDING + taskid, task)
        self.loop.call_soon(self._cleanup)
        return self.Task(self._decode(item), taskid)


    def get_last(self, blocking=False):
        '''
        :param: blocking :bool: -- block until a task is available
        Gets a teask from the rear of the queue
        Returns a Task object tuple (task, taskid)
        '''
        taskid = str(uuid.uuid4()).replace('-', '')
        if not blocking:
            item = self.r.rpop(self.Q)
        else:
            item = self.r.brpop(self.Q)
        if self.safemode and item is not None:
            task = {
                'task' : item,
                'timestamp' : time.time(),
                'taskid' : taskid
            }
            self.r.hmset(self.PENDING + taskid, task)
        self.loop.call_soon(self._cleanup)
        return self.Task(self._decode(item), taskid)


    def task_done(self, taskid):
        '''
        :param: taskid :str: -- the taskid pulled from the queue
        Notifies that a given task is completed and removes it
        from the task_pending queue.
        '''
        if not self.safemode:
            return
        self.r.delete(self.PENDING + taskid)
        self.loop.call_soon(self._cleanup)
        return taskid


    def task_reset(self, taskid):
        '''
        :param: taskid :str: -- the task id to re submit to the head of the queue
        Returns a task to the head of the queue
        '''
        if not self.safemode:
            return
        task = self.r.hmget(self.PENDING + taskid, 'task')[0].decode('ascii')
        if task:
            self.r.lpush(self.Q, task)
        self.loop.call_soon(self._cleanup)
        return


    def length(self):
        '''
        Returns the length of the queue
        '''
        self.loop.call_soon(self._cleanup)
        return int(self.r.llen(self.Q))


    def position(self, task):
        '''
        :param: item :any: -- the item to check the positon of
        Returns the position of an item in the queue
        '''
        self.loop.call_soon(self._cleanup)
        for t in range(self.r.llen(self.Q)):
            print(self.r.lindex(self.Q, t))
            if self.r.lindex(self.Q, t) == task.encode('ascii'):
                return t
        return -1


    def promote(self, index):
        '''
        :param: index :int: -- index of the item to promote to the front of the queue
        Promote a task to the top of the queue by index
        '''
        uid = str(uuid.uuid4())
        top = self.r.lindex(self.Q, 0)
        item = self.r.lindex(self.Q, index)
        self.r.linsert(self.Q, 'BEFORE', top, item)
        self.r.lset(self.Q, index + 1, uid)
        self.r.lrem(self.Q, 1, uid)
        self.loop.call_soon(self._cleanup)
        return

    def pending(self):
        '''
        Returns the number of pending tasks
        '''
        self.loop.call_soon(self._cleanup)
        num = 0
        for task in self.r.scan_iter(self.PENDING + '*'):
            num += 1
        self.loop.call_soon(self._cleanup)
        return num

    def drop(self, qname):
        '''
        :param: qname :str: -- the queue name, for security's sake.
        Clears the queue. This cannot be undone.
        '''
        self.r.delete('{}:q'.format(qname))
        return

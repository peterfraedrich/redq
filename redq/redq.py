#!/usr/bin/env python3

import redis
import time
import uuid

class RedisQueue:
    '''
    Implements a redis based queue using redis keys instead of pubsub.
    '''

    STATS = {
        'task_done' : 0,
        'task_added' : 0,
        'task_started' : 0,
        'task_pending' : 0,
        'task_ttl' : [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
        'q_length' : 0
    }

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
        self.decode = decode_strings
        self.qname = qname
        self.Q = '{}:q'.format(qname)
        self.GC = '{}:gc'.format(qname)
        self.PENDING = '{}:pending'.format(qname)
        self.r = redis.StrictRedis(host=redis_host, port=6379, db=redis_db, password=redis_auth)
        self.r.set('{}:queue_init'.format(qname), time.time())
        self.r.set(self.GC, time.time())
        return

    def _decode(self, bstr):
        '''
        :param: bstr :binary: -- decodes a binary string to ASCII if `decode_strings` is set to `True`
        '''
        if self.decode:
            return bstr.decode('ascii')
        else:
            return bstr

    def put(self, item):
        '''
        Pushes an item onto the queue
        :param: item :any: -- the item to push to the queue
        '''
        self.r.rpush(self.Q, item)
        return

    def get(self, blocking=False):
        '''
        :param: blocking :bool: -- Block until a task is available
        Gets a task from the queue
        Returns an UTF-8 encoded string
        '''
        if not blocking:
            item = self.r.lpop(self.Q)
        else:
            item = self.r.blpop(self.Q)
        return self._decode(item)

    def length(self):
        '''
        Returns the length of the queue
        '''
        return int(self.r.llen(self.Q))

    def position(self, task):
        '''
        :param: item :any: -- the item to check the positon of
        Returns the position of an item in the queue
        '''
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
        return

    def drop(self, qname):
        '''
        :param: qname :str: -- the queue name, for security's sake.
        Clears the queue. This cannot be undone.
        '''
        self.r.delete('{}:q'.format(qname))
        return

    # COME BACK TO THIS
    # def _get_stats(self):
    #     root = '{}:stats'.format(self.qname)
    #     stat = self.r.hmget(root, self.STATS)
    #     print(stat)
    #     return

    # def _set_stats(self):
    #     root = '{}:stats'.format(self.qname)
    #     self.r.hmset(root, self.STATS)
    #     return
    #

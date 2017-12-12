#!/usr/bin/env python3

import redis
import time
import uuid

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
        if self.decode:
            return bstr.decode('ascii')
        else:
            return bstr

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
        self.decode = decode_strings
        self.qname = qname
        self.Q = '{}:q'.format(qname)
        self.GC = '{}:gc'.format(qname)
        self.PENDING = '{}:pending'.format(qname)
        self.r = redis.StrictRedis(host=redis_host, port=6379, db=redis_db, password=redis_auth)
        self.r.set('{}:queue_init'.format(qname), time.time())
        self.r.set(self.GC, time.time())
        return


    def put(self, item):
        '''
        Pushes an item onto the queue
        :param: item :any: -- the item to push to the queue
        '''
        self.r.rpush(self.Q, item)
        return


    def put_first(self, item):
        '''
        :param: item :any: -- the item to push to the queue
        Pushes an item onto the front of the queue
        '''
        self.r.lpush(self.Q, item)
        return


    def get(self, blocking=False):
        '''
        :param: blocking :bool: -- Block until a task is available
        Gets a task from the queue
        Returns an ASCII encoded string
        '''
        if not blocking:
            item = self.r.lpop(self.Q)
        else:
            item = self.r.blpop(self.Q)
        return self._decode(item)


    def get_last(self, blocking=False):
        '''
        param: blocking :bool: -- block until a task is available
        Gets a teask from the rear of the queue
        Returns an ASCII string
        '''
        if not blocking:
            item = self.r.rpop(self.Q)
        else:
            item = self.r.brpop(self.Q)
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

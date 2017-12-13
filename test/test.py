#!/usr/bin/env python3

import redq
import uuid
import random
import json
import time

q = redq.RedisQueue(qname='redq')

def out(op, time):
    print('{},{},{}'.format(op, time, time.time()))

for loop in range(1):

    for put in range(50):
        test_obj = {}
        test_sobj = {}
        for i in range(random.randint(20,100)):
            test_obj[i] = str(uuid.uuid4())
        for i in range(random.randint(10,20)):
            test_sobj[i] = str(uuid.uuid4())

        test_obj['subobj'] = test_sobj
        start = time.time()
        q.put(json.dumps(test_obj))
        print('put:{}'.format(time.time() - start))

    for putf in range(50):
        test_obj = {}
        test_sobj = {}
        for i in range(random.randint(20,100)):
            test_obj[i] = str(uuid.uuid4())
        for i in range(random.randint(10,20)):
            test_sobj[i] = str(uuid.uuid4())

        test_obj['subobj'] = test_sobj
        start = time.time()
        q.put_first(json.dumps(test_obj))
        print('put_first:{}'.format(time.time() - start))

    for get in range(50):
        start = time.time()
        q.get()
        print('get:{}'.format(time.time() - start))

    for getl in range(50):
        start = time.time()
        q.get_last()
        print('get_last:{}'.format(time.time() - start))

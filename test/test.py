#!/usr/bin/env python3

from redq import redq

q = redq.RedisQueue(qname='redq')

q.put('1234')
q.put('123456')
q.put('something')
print('LEN: ', q.length())
print('POS: ', q.position('something'))
p = q.position('something')
q.promote(p)
print('ITEM: ', q.get())
print('LEN: ', q.length())
q.get()
q.get()
q.drop('redq')

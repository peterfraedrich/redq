# redq
A Redis-based message queue library, no server process required.

The idea was to create a Redis based queue library similar to Hotqueue but with some added features like a "safemode" (more on that later) and statistics tracking (coming soon). **redq** uses lists to store *tasks* on a first-in, first-out (FIFO) basis (except when using the `get_last` or `put_first` methods. Again, more on that later.)


## Installation
(pypi coming soon!)

```shell
$> pip install redq
```

## Usage

```python
import redq
r = redq.RedisQueue()
```

## Example

```python
>>> import redq

>>> r = redq.RedisQueue()

>>> r.put('Hello world')

>>> r.length()
1

>>> task = r.get()
Task(task='Hello world', taskid='e2fbd19fb0f74c18992ede1321348f85')

>>> print(task.task)
'Hello world'

>>> r.task_done(task.taskid)
'e2fbd19fb0f74c18992ede1321348f85'
```

## API Reference
```python
redq.RedisQueue(
    redis_host='localhost',
    redis_port=6379,
    redis_auth=None,
    redis_db=0,
    qname='redq',
    ttl=15,
    safemode=True,
    gc=True,
    decode_strings=True
)
    Parameters:
        redis_host = Redis host to connect to (default=localhost)
        redis_port = Port to connect to redis on (default=6379)
        redis_auth = Redis auth string (default=None [no auth])
        redis_db = database index to use for the queue (default=0)
        qname = customize the name of the queue (default='redq')
        ttl = threshold in minutes after which pending tasks are considered stale and pushed back to the top of the queue default=15)
        safemode = copies tasks to a pending queue on redq.RedisQueue.get() to ensure all tasks are handled (default=True)
        gc = enable/disable automatic cleanup of stale pending tasks back to the queue (default=True)
        decode_strings = automatically decode binary strings (default=True)

    Returns: Redis queue connection object.


redq.RedisQueue.put(task)

    Puts a task onto the queue.

    Parameters:
        task = the item to be put onto rear the queue

    Returns: None


redq.RedisQueue.put_first(task)

    Puts a task onto the front of the queue (index 0)

    Parameters:
        task = the item to be put into the front of the queue

    Returns: None


redq.RedisQueue.get(blocking=False)

    Gets a task from the queue.

    Parameters:
        blocking = block execution until a task is available on the queue (default=False)

    Returns: Task(task, taskid)


redq.RedisQueue.get_last(blocking=False)

    Gets a task from the rear of the queue.

    Parameters:
        blocking = block execution until a task is available on the queue (default=False)

    Returns: Task(task, taskid)


redq.RedisQueue.task_done(taskid)

    Notify the queue of a finished task. This only needs to be called if safemode is enabled, otherwise
    this method does nothing.

    Parameters:
        taskid = taskid that was returned from get() or get_last()

    Returns: taskid

redq.RedisQueue.task_reset(taskid)

    Manually push a task back to the top of the queue. This is useful for after handling exceptions
    and letting a different queue worker take the task instead of re-submitting the task to the
    rear of the queue.

    Parameters:
        taskid = taskid of the task that was returned from get() or get_last()


redq.RedisQueue.length()

    Get the length of the queue.

    Parameters: none

    Returns: integer


redq.RedisQueue.position(task)

    Get the position in line (index) of a given task.

    Parameters:
        task = the task to get the position of

    Returns: integer


redq.RedisQueue.promote(index)

    Promote a task from its current position to the front of the queue.

    Parameters:
        index = index of the task to promote

    Returns: None


redq.RedisQueue.pending()

    Get the number of pending tasks in the pending queue.

    Parameters: none

    Returns: integer


redq.RedisQueue.drop(qname)

    Drop the entire queue, clearing it back to zero.

    Parameters:
        qname = name of the queue, used here as a security measure

    Returns: none
```

### To Do
* Add stat counters 

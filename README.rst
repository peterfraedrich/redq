redq
====

A Redis-based message queue library, no server process required.

The idea was to create a Redis based queue library similar to
`Hotqueue <https://github.com/richardhenry/hotqueue>`__ but with some
added features like a "safemode" (more on that later) and statistics
tracking (coming soon). **redq** uses lists to store *tasks* on a
first-in, first-out (FIFO) basis (except when using the ``get_last`` or
``put_first`` methods. Again, more on that later.)

Installation
------------

(pypi coming soon!)

.. code:: shell

    $> pip install redq

Usage
-----

.. code:: python

    import redq
    r = redq.RedisQueue()

Example
-------

.. code:: python

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

Safemode and Garbage Collection
-------------------------------

Unique to ``redq`` is the idea of a ``safemode`` and background
cleanup/garbage collection. When safemode is enabled, any ``get()``
calls that would normally pop the task off the queue actually place the
task in a separate ``pending`` branch with a unique ``taskid`` and a
timestamp. This means that if the queue client errors out, or somehow
can't complete whatever task with the task object, the task is not lost.
This functionality is similar to the Python stdlib ``Queue`` where you
have to make an explicit ``task_done`` call. When safemode is enabled,
only a ``task_done()`` call will remove the task from the ``pending``
queue. When safemode is disabled, the original ``get()`` call will pop
the task without sending to ``pending``.

Corollary to this function, there is a cleanup/garbage collection
function that is triggered with most function calls that looks for
abandoned pending tasks and, if they are older than the given ``ttl``,
resubmits them to the top of the queue for processing. This ensures that
no task is left un-handled.

Both garbage collection and safemode are disable-able if you so choose.

API Reference
-------------

.. code:: python

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

To Do
~~~~~

-  Add stat counters
-  Sentinel support

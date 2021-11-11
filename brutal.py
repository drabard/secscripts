#!/usr/bin/env python3

import threading
import requests
import time
import queue

import sys

# >>>>>>>>>> INPUT SECTION
# Each thread will sleep for this period (in seconds) between process_variables
# calls.
PROCESS_DELAY = 0

# Number of threads used for sending requests in parallel.
NUM_THREADS = 24


def init_process_context(process_context):
    # process_context is a dictionary later available in process_variables.
    pass


def produce_variables():
    # This is a generator function yielding tuples of variables to be later
    # processed in process_variables.
    yield None


def process_variables(variables, process_context):
    # Put whatever you need here to be processed and return a result that will
    # later be processed in check_result.
    return None


def init_check_context(check_context):
    # check_context is a dictionary later available in check_result.
    pass


def check_result(result, check_context):
    # This is a function checking responses
    pass

# <<<<<<<<<<


# produce_variables and process_variables have this much time (in seconds) to
# create a new set of variables or a result respectively.
# If there is no new variable or result produced within this time, we assume
# the work is done.
EMPTY_QUEUE_TIMEOUT = 2

# Maximum size of the queues used to communicate between threads.
QUEUE_MAX_SIZE = 10000


def produce_vars(vars_queue):
    for vs in produce_variables():
        vars_queue.put(vs)


def consume_vars(vars_queue, res_queue):
    thread_context = {}
    init_process_context(thread_context)
    while True:
        try:
            variables = vars_queue.get(timeout=EMPTY_QUEUE_TIMEOUT)
            resp = process_variables(variables, thread_context)
            res_queue.put(resp)
            vars_queue.task_done()
            time.sleep(PROCESS_DELAY)
        except queue.Empty:
            return


def consume_result(res_queue):
    thread_context = {}
    init_check_context(thread_context)
    while True:
        try:
            result = res_queue.get(timeout=EMPTY_QUEUE_TIMEOUT)
            check_result(result, thread_context)
            res_queue.task_done()
        except queue.Empty:
            return


if __name__ == '__main__':
    vars_queue = queue.Queue(maxsize=QUEUE_MAX_SIZE)
    res_queue = queue.Queue(maxsize=QUEUE_MAX_SIZE)

    var_producer_thread = threading.Thread(
        target=produce_vars, args=(vars_queue,))
    var_producer_thread.start()

    var_consumer_threads = [threading.Thread(target=consume_vars,
                                             args=(vars_queue, res_queue))
                            for _ in range(NUM_THREADS)]
    for cthread in var_consumer_threads:
        cthread.start()

    res_consumer_thread = threading.Thread(
        target=consume_result, args=(res_queue,)
    )
    res_consumer_thread.start()

    var_producer_thread.join()
    vars_queue.join()
    for cthread in var_consumer_threads:
        cthread.join()
    res_queue.join()
    res_consumer_thread.join()

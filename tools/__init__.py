from logging import FileHandler
from logging.handlers import QueueHandler
from logging.handlers import QueueListener
import logging
import logging
from logging.handlers import QueueHandler
from logging.handlers import QueueListener
from logging import StreamHandler
from random import random
from queue import Queue

from queue import Queue
import logging
import asyncio
async def init_logger():
    # get the root logger
    log = logging.getLogger("spf_lookup")
    # create the shared queue
    que = Queue()
    # add a handler that uses the shared queue
    log.addHandler(QueueHandler(que))
    # log all messages, debug and up
    log.setLevel(logging.DEBUG)
    logging.basicConfig(format='%(asctime)s [%(levelname)s] - %(message)s', level=logging.DEBUG, filename='spf.log')
    # create a listener for messages on the queue
    listener = QueueListener(que, StreamHandler())
    try:
        # start the listener
        listener.start()
        # report the logger is ready
        logging.debug(f'Logger has started')
        # wait forever
        while True:
            await asyncio.sleep(60)
    finally:
        # report the logger is done
        logging.debug(f'Logger is shutting down')
        # ensure the listener is closed
        listener.stop()


# reference to the logger task
LOGGER_TASK = None


# coroutine to safely start the logger
async def safely_start_logger():
    # initialize the logger
    LOGGER_TASK = asyncio.create_task(init_logger())
    # allow the logger to start
    await asyncio.sleep(0)
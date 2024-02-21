import asyncio
import anyio
import sys
from tqdm.asyncio import trange, tqdm, tqdm_asyncio
import aiodns
import aiofiles  # import the aiofiles module
import logging
from logging import FileHandler
from logging.handlers import QueueHandler
from logging.handlers import QueueListener
from random import random
from queue import Queue


# import click
import asyncclick as click
from functools import wraps

background=False
activity_log='activity.log'

@click.command()
@click.option('--input_file', 'filename', required=True, type=str, help='Input file.')
@click.option('--start_at', 'start_at', required=False, type=int, default=0, help='Chunk to start (including)  querying at.')
@click.option('--stop_at', 'stop_at', required=False, type=int, default=0, help='Chunk to stop (including) querying at.')
@click.option('--chunk_size', 'chunk_size', required=False, type=int, default=2500, help='Chunk size.')
@click.option('--concur', 'concur', required=False, type=int, default=10, help='Concurrency limit.')
@click.option('--activity_log', 'a_log', required=False, type=str, default='activity.log', help='Activity log file when running in background mode')
@click.option('--background', 'bg_flag', is_flag=True, default=False, help='Enable or disable background mode.')
async def cli(filename, start_at, stop_at, a_log, bg_flag, concur, chunk_size):
    background = bg_flag
    activity_log = a_log
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    if background:
        print ('Running as a background task. check the activity log for status')
    domains = get_domains_from_file(filename)

    domain_list = split_list_by_size(domains, chunk_size)

    c = 0
    t = len(domain_list) + 1
    f = open("count.txt", "w")
    f.write(str(t) + '\n')
    f.close()
    f = open("arguments.txt", "w")
    f.write(' '.join(sys.argv[1:]) + '\n')
    f.close()

    for domain in domain_list:
        resolver = DnsResolver(nameservers=['1.1.1.1', '9.9.9.9', '1.0.0.1', '149.112.112.9'], limit=concur,
                               output=f'./export/export_{c:03}.txt')  # use the limit parameter to control concurrent tasks
        resolver.background = background
        c = c + 1
        if stop_at == 0:
            stop_at = t
        if c >= start_at and c <= stop_at:
            resolver.info_text = f'Domain list {c:03}/{t}'
            asyncio.run(resolver.query(domain))
            asyncio.run(resolver.query(domain))
        else:
            # tqdm.write("Skipping chunk #" + str(c) + " of " + str(t))
            pass


async def init_logger(log_file):
    # get the root logger
    log = logging.getLogger()
    # create the shared queue
    que = Queue()
    # add a handler that uses the shared queue
    log.addHandler(QueueHandler(que))
    # log all messages, debug and up
    log.setLevel(logging.DEBUG)
    # create the file handler for logging
    file_handler = FileHandler(log_file)
    # create a listener for messages on the queue
    listener = QueueListener(que, file_handler)
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

class DnsResolver:
    def __init__(self, nameservers, limit=100, output='export.txt',
                 info_text=''):  # set default concurrency limit to 100
        self.nameservers = nameservers
        self.size = 0
        self.semaphore = asyncio.Semaphore(limit)
        self.output_file = output
        self.info_text = info_text
        self.background=False

    async def do_query(self, domain, record_type='TXT'):
        if self.background is True:
            pass
            # async with aiofiles.open(activity_log, mode='a') as l:
                # await l.write("> "+domain+'\n')
        async with self.semaphore:
            try:
                resolver = aiodns.DNSResolver(nameservers=self.nameservers, loop=asyncio.get_event_loop(), timeout=5)
                r = await resolver.query(domain, record_type)
            except Exception as e:
                return {'domain': domain, 'result': None}
            return {'domain': domain, 'result': r}

    async def query(self, domains, record_type='TXT'):

        self.size = len(domains)
        tasks = [self.do_query(domain, record_type) for domain in domains]
        if self.background:
            responses = await asyncio.gather(*tasks)
        else:
            responses = await tqdm_asyncio.gather(*tasks, ncols=105, desc=self.info_text)
        async with aiofiles.open(activity_log, mode='a') as l:
            async with aiofiles.open(self.output_file, mode='w') as f:
                for response in responses:
                    try:
                        if response['result']:
                            for entry in response['result']:
                                result_line = f'TXT,{entry.text},{response["domain"]}\n'
                                if background is True:
                                        await l.write('< '+response["domain"]+'\n')
                                await f.write(result_line)

                    except Exception as e:
                        print(f'{e}')
                        pass


def get_domains_from_file(filename):
    lines = []
    with open(filename, 'r') as file:
        for line in file:
            try:
                l, m = line.split(',')
                m = m.strip()
                lines.append(m)
            except ValueError as e:
                print(f"Exception {str(e)}, {line}")

        return lines


def split_list(input_list, parts):
    avg = len(input_list) // parts
    remainder = len(input_list) % parts
    return [input_list[i * avg + min(i, remainder):(i + 1) * avg + min(i + 1, remainder)] for i in range(parts)]

def split_list_by_size(input_list, slice_size):
    return [input_list[i * slice_size:(i + 1) * slice_size] for i in range((len(input_list) + slice_size - 1) // slice_size )]


if __name__ == '__main__':
    asyncio.run(cli())


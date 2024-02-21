import asyncio
import logging
import sys
from tqdm.asyncio import trange, tqdm, tqdm_asyncio
import aiodns
import aiofiles

import click

background = False
activity_log = 'activity.log'
# logging is blocking - use it wisely..
logging.basicConfig(format='%(asctime)s [%(levelname)s] - %(message)s', level=logging.CRITICAL, filename='spf.log')
logger = logging.getLogger("spf_lookup")
logger.setLevel(logging.DEBUG)

@click.command()
@click.option('--input_file', 'filename', required=True, type=str, help='Input file.')
@click.option('--start_at', 'start_at', required=False, type=int, default=0,
              help='Chunk to start (including)  querying at.')
@click.option('--stop_at', 'stop_at', required=False, type=int, default=0,
              help='Chunk to stop (including) querying at.')
@click.option('--chunk_size', 'chunk_size', required=False, type=int, default=2500, help='Chunk size.')
@click.option('--concur', 'concur', required=False, type=int, default=10, help='Concurrency limit.')
@click.option('--activity_log', 'a_log', required=False, type=str, default='activity.log',
              help='Activity log file when running in background mode')
@click.option('--background', 'bg_flag', is_flag=True, default=False, help='Enable or disable background mode.')
def cli(filename, start_at, stop_at, a_log, bg_flag, concur, chunk_size):
    logger.info(f'======= Starting async_lookup.py {' '.join(sys.argv[1:])} ======= ')
    background = bg_flag
    activity_log = a_log
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        logger.debug("Running on Windows")
    if background:
        print('Running as a background task. check the activity log for status')
    domains = get_domains_from_file(filename)
    domain_list = domains
    resize = False
    logger.debug(f'Start-Stop {start_at}-{stop_at}')
    if start_at > 0 and stop_at == 0:
        stop_at = len(domain_list)
        resize = True
    elif stop_at == 0 and start_at > 0:
        start_at = 0
        resize = True
    elif stop_at > 0 and start_at > 0:
        resize = True

    domain_list = split_by_index(domain_list, start_at, stop_at) if resize else domain_list
    domain_list = split_list_by_size(domain_list, chunk_size)
    logger.info(f'Number of domains {len(domain_list)}: From: {start_at} - To {stop_at}')

    t = len(domain_list) + 1

    c = 0

    f = open("count.txt", "w")
    f.write(str(t) + '\n')
    f.close()
    f = open("arguments.txt", "w")
    f.write(' '.join(sys.argv[1:]) + '\n')

    f.close()

    for domain_chunk in domain_list:
        dns_resolver = DnsResolver(nameservers=['1.1.1.1', '9.9.9.9', '1.0.0.1', '149.112.112.9'], limit=concur,
                                   output=f'./export/export_{c:010}.txt')
        dns_resolver.background = background
        c = c + 1
        if stop_at == 0:
            stop_at = t
        dns_resolver.info_text = f'Domain list {c:03}/{t}'
        asyncio.run(dns_resolver.query(domain_chunk))


class DnsResolver:
    def __init__(self, nameservers, limit=100, output='export.txt',
                 info_text=''):  # set default concurrency limit to 100
        self.nameservers = nameservers
        self.size = 0
        self.semaphore = asyncio.Semaphore(limit)
        self.output_file = output
        self.info_text = info_text
        self.background = False

    async def do_query(self, domain, record_type='TXT'):
        if self.background is True:
            pass
        async with self.semaphore:
            try:
                resolver = aiodns.DNSResolver(nameservers=self.nameservers, loop=asyncio.get_event_loop(), timeout=5)
                r = await resolver.query(domain, record_type)
            except Exception as e:
                return {'domain': domain, 'result': None}
                logger.critical(f'Exception: Failed to Query Domain {domain} for type {record_type}: {e}')
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
                                    await l.write('< ' + response["domain"] + '\n')
                                await f.write(result_line)

                    except Exception as e:
                        print(f'{e}')
                        logger.critical(f'Exception writing result data: {e}')
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
                logger.debug(f'Format problem while reading input data: {str(e)} : {line}')
            except Exception as e:
                logger.critical(f'Exception Get Domains from File: {str(e)} : {line}')

        return lines


def split_by_index(input_list, start_at, end_at):
    # Convert 1-indexed to 0-indexed for Python lists
    start_at -= 1
    end_at -= 1
    # Return the slice
    return input_list[start_at: end_at + 1]


def split_list(input_list, parts):
    avg = len(input_list) // parts
    remainder = len(input_list) % parts
    return [input_list[i * avg + min(i, remainder):(i + 1) * avg + min(i + 1, remainder)] for i in range(parts)]


def split_list_by_size(input_list, slice_size):
    return [input_list[i * slice_size:(i + 1) * slice_size] for i in
            range((len(input_list) + slice_size - 1) // slice_size)]


if __name__ == '__main__':
    cli()

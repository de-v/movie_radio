import os
import logging
import asyncio
import sys
import getopt

import aiohttp
from aioredis import create_redis
from config.settings import STREAM_PORT, STREAM_HOST


# icacast metadata file location
METADATA_FILE = 'status-json.xsl'

server_logger = logging.getLogger('aiohttp.server')


def main(host, port):
    server_logger.info('Got params connection host {0}, port {1}'.format(host, port))
    loop = asyncio.get_event_loop()
    title = None
    redis = loop.run_until_complete(create_redis(('localhost', 6379)))
    while True:
        new_title = loop.run_until_complete(get_current_song(host, port))
        if new_title != title:
            loop.run_until_complete(redis.publish('CHANNEL', new_title))
            title = new_title
    loop.close()
    return False


async def get_current_song(icecast_host, icecast_port):
    """
    Args:
        icecast_host: host where Icecast 2 server running
        icecast_port: port of Icecast 2 server

    Returns: current song if it is possible, None if not

    """
    if icecast_port:
        icecast_host = ':'.join([icecast_host, icecast_port])
    icecast_host = '/'.join([icecast_host, METADATA_FILE])
    try:
        with aiohttp.ClientSession() as client:
            response = await client.request('GET', icecast_host)
        body = await response.json()
    except Exception as e:
        server_logger.error('Error occurred while getting response from icecast {}!'.format(str(e)))
        return None
    try:
        title = body['icestats']['source'].get('title')
    except KeyError:
        return None

    return title


if __name__ == '__main__':
    """
    in case if script is executed standalone we need to
    have ability to import settings from project if script is executed on the same
    machine as app
    If no - use  default values
    """
    project_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    sys.path.append(project_path)
    opts, args = getopt.getopt(sys.argv[1:], shortopts="h:p:", longopts=['host', 'port'])
    try:
        if opts:
            for opt, arg in opts:
                if opt in ['h', 'host']:
                    host = arg
                elif opt in ['p', 'port']:
                    port = arg
            logging.info('Using settings from sys args')
        else:
            host, port = STREAM_HOST, STREAM_PORT
        main(port=port, host=host)
    except KeyboardInterrupt:
        logging.info('Task finished!')

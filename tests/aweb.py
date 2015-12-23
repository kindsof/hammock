#! /usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function
from tests import resources
import sys
import asyncio
import hammock


import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


# flake8: noqa
# python3.5 syntax from here

async def init(loop, port):
    # pylint: disable=undefined-variable
    _hammock = hammock.Hammock('aiohttp', resources, loop=loop, debug=True)
    srv = await loop.create_server(_hammock.api.make_handler(), 'localhost', port)
    print('Server started at http://localhost:{}'.format(port))
    return srv


if __name__ == '__main__':
    PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    LOOP = asyncio.get_event_loop()
    LOOP.run_until_complete(init(LOOP, PORT))
    try:
        LOOP.run_forever()
    except KeyboardInterrupt:
        pass

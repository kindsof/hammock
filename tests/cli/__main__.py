from __future__ import absolute_import
import sys
import logging
import tests.cli.base as base


LOG = logging.getLogger(__name__)


if __name__ == '__main__':
    LOG.info('Starting server...')
    process = base.server()
    try:
        base.cli(argv=sys.argv[1:], remove_ignored_commands=False, stdout=sys.stdout)
    finally:
        LOG.info('Killing server...')
        base.kill_server(process)

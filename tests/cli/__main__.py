from __future__ import absolute_import
import sys
import logging
import tests.cli.base as base
import tests.uwsgi_base as uwsgi_base


LOG = logging.getLogger(__name__)


if __name__ == '__main__':
    LOG.info('Starting server...')
    PROCESS, _ = uwsgi_base.start_server(base.PORT, base.__file__.replace('.pyc', '.py'))
    try:
        base.cli(argv=sys.argv[1:], remove_ignored_commands=False, stdout=sys.stdout)
    finally:
        LOG.info('Killing server...')
        PROCESS.terminate()

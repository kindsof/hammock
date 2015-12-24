#! /user/bin/env python
from __future__ import absolute_import
from __future__ import print_function
import hammock
import sys
import subprocess
import tests.resources as resources
import os

HAMMOCK = hammock.Hammock(os.environ['BACKEND'], resources)
API = HAMMOCK.api


def command(listen_port):
    return [
        'uwsgi',
        '--http', ':{:d}'.format(listen_port),
        '--wsgi-file', __file__.replace('.pyc', '.py'),
        '--callable', 'API',
        '--need-app',
        '--procname', 'hammock-test',
    ]

COMMAND_LINE_ARGS = [
    '--py-auto-reload', '1',
    '--honour-stdin',
]

if __name__ == '__main__':
    PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    ARGS = command(PORT) + COMMAND_LINE_ARGS
    print(' '.join(ARGS))
    subprocess.check_output(ARGS)

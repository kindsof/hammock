#! /user/bin/env python
from __future__ import absolute_import
import falcon
import hammock
import sys
import subprocess
import tests.resources as resources

application = falcon.API()
hammock.Hammock(application, resources)


def command(listen_port):
    return [
        'uwsgi',
        '--http', ':{:d}'.format(listen_port),
        '--wsgi-file', __file__.replace('.pyc', '.py'),
        '--need-app',
        '--procname', 'hammock-test',
    ]

COMMAND_LINE_ARGS = [
    '--py-auto-reload', '1',
    '--honour-stdin',
]

if __name__ == '__main__':
    port = sys.argv[1]
    subprocess.check_output(command(port) + COMMAND_LINE_ARGS)

#! /user/bin/env python
from __future__ import absolute_import
import falcon
import hammock
import sys
import subprocess
import tests.resources as resources

application = falcon.API()
hammock.Hammock(application, resources)


def command(port):
    return [
        'uwsgi',
        '--http', ':{:d}'.format(port),
        '--wsgi-file', __file__.replace('.pyc', '.py'),
        '--honour-stdin',
        '--need-app',
        '--py-auto-reload', '1',
        '--procname', 'hammock-test',
    ]


if __name__ == '__main__':
    subprocess.check_output(command(sys.argv[1]))

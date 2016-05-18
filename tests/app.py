#! /user/bin/env python
from __future__ import absolute_import
import os
import hammock
import sys
import subprocess
import tests.resources1 as resources1
import tests.base as tests_base


api = hammock.Hammock(
    'falcon', resources1,
    policy_file=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'policy.json'),
    credentials_class=tests_base.TestCredentials,
)
application = api.api  # pylint: disable=invalid-name


THIS_FILE = os.path.abspath(__file__.replace('.pyc', '.py'))


def command(listen_port, app_file=None, procname='hammock-test'):
    app_file = app_file or THIS_FILE
    return [
        'uwsgi',
        '--http', ':{:d}'.format(listen_port),
        '--wsgi-file', app_file,
        '--need-app',
        '--procname', procname,
    ]


COMMAND_LINE_ARGS = [
    '--py-auto-reload', '1',
    '--honour-stdin',
]


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000  # pylint: disable=invalid-name
    subprocess.check_output(command(port) + COMMAND_LINE_ARGS)

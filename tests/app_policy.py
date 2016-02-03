#! /user/bin/env python
from __future__ import absolute_import
import os
import falcon
import hammock
import tests.resources as resources


application = falcon.API()  # pylint: disable=invalid-name
hammock.Hammock(
    application, resources,
    policy_file=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'policy.json')
)


def command(listen_port):
    return [
        'uwsgi',
        '--http', ':{:d}'.format(listen_port),
        '--wsgi-file', __file__.replace('.pyc', '.py'),
        '--need-app',
        '--procname', 'hammock-test',
    ]

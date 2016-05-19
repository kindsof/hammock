from __future__ import absolute_import
import StringIO
import importlib
import json
import logging
import os
import subprocess
import sys
import falcon

import hammock
import hammock.cli
import hammock.client as client
import hammock.testing as testing

import tests.uwsgi_base as uwsgi_base

PORT = testing.get_available_port()
LOG = logging.getLogger(__name__)
BUILD_PATH = 'build/cli-tests'


#
#  Generate clients file, and load their classes into variables
#

def get_unified_client(build_path):
    if not os.path.exists(build_path):
        os.makedirs(build_path)
    sys.path.append(build_path)
    client_map = {}
    for i in range(1, 3):
        with open('{}/client{}.py'.format(build_path, i), 'w') as file_object:
            file_object.write(client.ClientGenerator(
                'Client',
                importlib.import_module('tests.resources{}'.format(i))
            ).code + '\n')
        client_map['client{}'.format(i)] = getattr(importlib.import_module('client{}'.format(i)), 'Client')

    class Client(object):

        def __init__(self, *args, **kwargs):
            self.client1 = client_map['client1'](*args, **kwargs)
            self.client2 = client_map['client2'](*args, **kwargs)

    return Client


def get_unified_resources_package(build_path):
    if not os.path.exists(build_path):
        os.mkdir(build_path)
    resources_path = '{}/resources/'.format(build_path)
    if not os.path.exists(resources_path):
        os.mkdir(resources_path)
    sys.path.append(build_path)
    for i in range(1, 3):
        subprocess.check_output('cp -r tests/resources{}/* {}'.format(i, resources_path), shell=True)
    return importlib.import_module('resources')


UnifiedClient = get_unified_client(BUILD_PATH)
application = falcon.API()
hammock.Hammock(application, get_unified_resources_package('build/cli-tests'), policy_file=os.path.abspath('tests/policy.json'))


def cli(argv=sys.argv[1:], remove_ignored_commands=True, stdout=sys.stdout):
    app_class = type('App', (hammock.cli.App, ), {'REMOVE_COMMANDS_WITH_NAME_FALSE': remove_ignored_commands})
    return app_class(UnifiedClient, stdout=stdout).run(['--url', 'http://localhost:{}'.format(PORT)] + argv)


class Base(uwsgi_base.UwsgiBase):

    PORT = PORT
    app_module = __file__.replace('.pyc', '.py')

    def run_command(self, command, remove_ignored_commands=True):
        out = StringIO.StringIO()
        if not isinstance(command, list):
            command = command.split(' ')
        return_code = cli(command, remove_ignored_commands=remove_ignored_commands, stdout=out)
        if return_code != 0:
            raise hammock.cli.CLIException('Error code {} from running command {}'.format(return_code, command))
        return out.getvalue()

    def run_json_command(self, command, remove_ignored_commands=True):
        if isinstance(command, list):
            command += ['-f', 'json']
        else:
            command += ' -f json'
        return json.loads(self.run_command(command, remove_ignored_commands=remove_ignored_commands))

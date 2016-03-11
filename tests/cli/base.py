from __future__ import absolute_import
import StringIO
import functools
import importlib
import json
import logging
import os
import socket
import subprocess
import sys
import unittest
import waiting
import falcon

import hammock
import hammock.cli
import hammock.client as client

PORT = '6543'
LOG = logging.getLogger(__name__)
BUILD_PATH = 'build/cli-tests'


class CLIException(Exception):
    pass


#
#  Generate clients file, and load their classes into variables
#

def get_clients(build_path):
    if not os.path.exists(build_path):
        os.makedirs(build_path)
    sys.path.append(build_path)
    client_list = []
    for i in range(1, 3):
        with open('{}/client{}.py'.format(build_path, i), 'w') as file_object:
            file_object.write(client.ClientGenerator(
                'Client',
                importlib.import_module('tests.resources{}'.format(i))
            ).code)
        client_list.append(getattr(importlib.import_module('client{}'.format(i)), 'Client'))
    return client_list


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


clients = get_clients(BUILD_PATH)
API = falcon.API()
hammock.Hammock(API, get_unified_resources_package('build/cli-tests'), policy_file=os.path.abspath('tests/policy.json'))


def cli(argv=sys.argv[1:], remove_ignored_commands=True, stdout=sys.stdout):
    app_class = type('App', (hammock.cli.App, ), {'REMOVE_COMMANDS_WITH_NAME_FALSE': remove_ignored_commands})
    return app_class(clients, stdout=stdout).run(['http://localhost:{}'.format(PORT)] + argv)


def server():
    server_proc = subprocess.Popen(
        ['uwsgi', '--http', ':{}'.format(PORT), '--yaml', 'tests/cli/uwsgi.yml'],
    )
    try:
        LOG.info('Waiting for server...')
        waiting.wait(
            functools.partial(socket.create_connection, ('localhost', PORT)),
            timeout_seconds=10, sleep_seconds=1,
            expected_exceptions=(socket.error, ),
        )
        LOG.info('server is up!')
    except:
        kill_server(server_proc)
    return server_proc


def kill_server(proc):
    proc.send_signal(9)
    proc.wait()


class Base(unittest.TestCase):

    server = None

    @classmethod
    def setUpClass(cls):
        cls.server = server()

    @classmethod
    def tearDownClass(cls):
        kill_server(cls.server)

    def run_command(self, command, remove_ignored_commands=True):
        out = StringIO.StringIO()
        return_code = cli(command.split(' '), remove_ignored_commands=remove_ignored_commands, stdout=out)
        if return_code != 0:
            raise CLIException('Error code {} from running command {}'.format(return_code, command))
        return out.getvalue()

    def run_json_command(self, command, remove_ignored_commands=True):
        return json.loads(self.run_command(command + ' -f json', remove_ignored_commands=remove_ignored_commands))

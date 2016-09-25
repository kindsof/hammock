from __future__ import absolute_import
import os
import signal
import subprocess
import unittest
import waiting
import functools
import hammock.testing as testing
import tests.app as app
import tests.test_client as test_client


def start_server(port, app_module=None, log_file_name=None, procname='hammock-test'):
    args = app.command(port, app_module, procname)
    kwargs = {}
    log_file = None
    if log_file_name:
        log_file = open(log_file_name, 'w')
        args += ['--logger', 'file:{}'.format(log_file_name)]
        kwargs = {'stderr': log_file, 'stdout': log_file}

    server = subprocess.Popen(args, **kwargs)
    waiting.wait(
        functools.partial(testing.test_connection, ("localhost", port)),
        timeout_seconds=10,
        waiting_for="server to start listening",
    )
    return server, log_file


class UwsgiBase(unittest.TestCase):
    PORT = testing.get_available_port()
    TOKEN = "token"
    _server = None
    _client = None
    app_module = None
    _server_log = None

    @classmethod
    def setUpClass(cls):
        if not os.path.exists('build/logs'):
            os.makedirs('build/logs')
        log_file_name = 'build/logs/server-{}.log'.format(cls.__name__.lower())
        proc_name = cls.__name__.lower()
        cls._server, cls._server_log = start_server(
            cls.PORT, cls.app_module, log_file_name, proc_name)

    @classmethod
    def tearDownClass(cls):
        os.kill(cls._server.pid, signal.SIGKILL)
        if cls._server_log:
            cls._server_log.close()

    def setUp(self):
        self._client = test_client.get_client(
            url="http://localhost:{}".format(self.PORT), token=self.TOKEN, retries=10)

    def get_client(self, **kwargs):
        return test_client.get_client(url="http://localhost:{}".format(self.PORT), **kwargs)

    def tearDown(self):
        self._client.close()
        self._client = None

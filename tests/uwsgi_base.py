from __future__ import absolute_import
import os
import subprocess
import unittest
import waiting
import functools
import hammock.testing as testing
import tests.app as app
import tests.test_client as test_client


class UwsgiBase(unittest.TestCase):
    PORT = 7001
    TOKEN = "token"
    _server = None
    _client = None
    app_module = app
    _server_log = None

    @classmethod
    def setUpClass(cls):
        if not os.path.exists('build/logs'):
            os.mkdir('build/logs')
        cls._server_log = open('build/logs/server-{}.log'.format(cls.__name__.lower()), 'w')
        subprocess.call(["pkill", "-9", "uwsgi"])
        cls._server = subprocess.Popen(
            cls.app_module.command(cls.PORT),
            stderr=cls._server_log, stdout=cls._server_log,
        )
        waiting.wait(
            functools.partial(testing.test_connection, ("localhost", cls.PORT)),
            timeout_seconds=10,
            waiting_for="server to start listening",
        )

    @classmethod
    def tearDownClass(cls):
        cls._server.terminate()
        cls._server_log.close()

    def setUp(self):
        self._client = test_client.get_client("localhost", self.PORT, token=self.TOKEN)

    def get_client(self, **kwargs):
        return test_client.get_client("localhost", self.PORT, **kwargs)

    def tearDown(self):
        self._client.close()
        self._client = None

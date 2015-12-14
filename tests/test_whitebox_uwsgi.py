from __future__ import absolute_import
import six
import subprocess
import unittest
import logging
import waiting
import functools
import hammock.types as types
import hammock.testing as testing
import tests.app as app
import tests.test_client as test_client


class TestWhiteboxUWSGI(unittest.TestCase):
    PORT = 7001
    TOKEN = "token"

    @classmethod
    def setUpClass(cls):
        subprocess.call(["pkill", "-9", "uwsgi"])
        cls._server = subprocess.Popen(app.command(cls.PORT))
        waiting.wait(
            functools.partial(testing.test_connection, ("localhost", cls.PORT)),
            timeout_seconds=10,
            waiting_for="server to start listening",
        )
        cls._client = test_client.get_client("localhost", cls.PORT, token=cls.TOKEN)

    @classmethod
    def tearDownClass(cls):
        cls._client.close()
        cls._server.terminate()

    def test_files(self):
        size_mb = 100
        content_length = size_mb << 20

        logging.info("Sending %dmb to server", size_mb)
        file_object = types.File(
            six.BytesIO(bytearray(content_length)),
            content_length,
        )
        response = self._client.files.check_size(file_object, size_mb)
        self.assertEqual(response, "OK")

        logging.info("Reading %dmb from server", size_mb)
        response = self._client.files.generate(size_mb)
        data = response.read()
        self.assertEqual(data.__sizeof__() >> 20, size_mb)

        logging.info("Echoing %dmb with server", size_mb)
        data = bytearray(content_length)
        file_object = types.File(six.BytesIO(data), content_length)
        response = self._client.files.echo(file_object)
        response_data = list(response.stream())
        response_data = six.b('').join(response_data)
        self.assertEqual(data, response_data)

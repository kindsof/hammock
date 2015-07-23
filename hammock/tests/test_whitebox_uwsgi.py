import subprocess
import unittest
import falcon
import logging
import StringIO as string_io
import waiting
import functools
import hammock
import hammock.tests.resources as resources
import hammock.client as client
import hammock.tests.server as server


api = falcon.API()
hammock.Hammock(api, resources)


exec client.ClientGenerator("TestClient", resources).code  # pylint: disable=exec-used
TestClient = locals()["TestClient"]


class TestWhiteboxUWSGI(unittest.TestCase):

    PORT = 7001
    TOKEN = "token"
    WORKLOAD_COUNT = 50

    @classmethod
    def setUpClass(cls):
        subprocess.Popen(["pkill", "-9", "uwsgi"]).communicate()
        api_name = [name for name, attr in globals().iteritems() if attr == api][0]
        file_name = __file__.replace(".pyc", ".py")
        cls._server = subprocess.Popen([
            "uwsgi", "--http", ":%d" % cls.PORT,
            "--wsgi-file", file_name,
            "--callable", api_name,
        ])
        waiting.wait(
            functools.partial(server.test_connection, ("localhost", cls.PORT)),
            timeout_seconds=10,
            waiting_for="server to start listening",
        )
        cls._client = TestClient("localhost", cls.PORT, cls.TOKEN)

    @classmethod
    def tearDownClass(cls):
        cls._client.close()
        cls._server.terminate()

    def test_files(self):
        size_mb = 100

        logging.info("Sending %dmb to server", size_mb)
        file_object = string_io.StringIO(bytearray(size_mb << 20))
        response = self._client.files.check_size(file_object, size_mb)
        self.assertEqual(response, "OK")

        logging.info("Reading %dmb from server", size_mb)
        response = self._client.files.generate(size_mb)
        data = response.read()
        self.assertEqual(data.__sizeof__() >> 20, size_mb)

        logging.info("Echoing %dmb with server", size_mb)
        file_object = string_io.StringIO(bytearray(int(size_mb) << 20))
        response = self._client.files.echo(file_object)

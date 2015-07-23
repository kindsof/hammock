import unittest
import tempfile
import os
import sys
import shutil
import hammock.client as client
import tests.resources as resources


def get_client():
    path = tempfile.mkdtemp()
    open(os.path.join(path, "client.py"), "w").write(client.ClientGenerator("TestClient", resources).code)
    open(os.path.join(path, "__init__.py"), "w")
    sys.path.append("/tmp")
    Client = __import__("%s.client" % path.strip("/").split("/")[1]).client.TestClient
    return Client("http://example.com", 8080)


class TestClient(unittest.TestCase):

    def setUp(self):
        self._client = get_client()

    def tearDown(self):
        # remove temporary directory of client code
        shutil.rmtree(os.path.join("/tmp", self._client.__module__.rsplit(".", 1)[0].replace(".", "/")))

    def test_client(self):
        self.assertTrue(hasattr(self._client, "dict"))
        self.assertTrue(hasattr(self._client, "text"))
        self.assertTrue(hasattr(self._client, "headers"))
        self.assertTrue(hasattr(self._client.dict, "item_create"))
        self.assertTrue(hasattr(self._client.dict, "item_get"))
        self.assertTrue(hasattr(self._client.dict, "item_change"))
        self.assertTrue(hasattr(self._client.dict, "item_delete"))
        self.assertTrue(hasattr(self._client.text, "upper"))
        self.assertTrue(hasattr(self._client.text, "replace"))
        self.assertTrue(hasattr(self._client.text, "replace_put"))
        self.assertTrue(hasattr(self._client.text, "replace_post"))
        self.assertTrue(hasattr(self._client.text, "replace_delete"))

        self.assertTrue(hasattr(self._client, "sub_resource"))
        self.assertTrue(hasattr(self._client.sub_resource, "sub"))
        self.assertTrue(hasattr(self._client.sub_resource, "sub2"))
        self.assertTrue(hasattr(self._client.sub_resource, "nested"))
        self.assertTrue(hasattr(self._client.sub_resource.nested, "sub"))
        self.assertTrue(hasattr(self._client, "sub_resource2"))
        self.assertTrue(hasattr(self._client.sub_resource2, "sub"))
        self.assertTrue(hasattr(self._client, "different_path"))

from __future__ import absolute_import
import unittest
import importlib
import os
import sys
import hammock.client as client
import tests.resources as resources


def get_client(*args, **kwargs):
    if not os.path.exists('build'):
        os.mkdir('build')
    with open('build/hammock_client.py', 'w') as client_file:
        client_file.write(client.ClientGenerator("HammockClient", resources).code)
    sys.path.append('build')
    client_class = importlib.import_module("hammock_client").HammockClient
    return client_class(*args, **kwargs)


class TestClient(unittest.TestCase):

    def setUp(self):
        self._client = get_client("http://example.com", 8080)

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

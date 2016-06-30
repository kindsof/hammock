from __future__ import absolute_import
import unittest
import importlib
import os
import sys
import fcntl
import hammock.client as client
import tests.resources1 as resources1


def get_client(*args, **kwargs):
    if not os.path.exists('build'):
        os.mkdir('build')
    client_file = open('build/hammock_client.py', 'w')
    try:
        fcntl.flock(client_file.fileno(), fcntl.LOCK_EX)
        client_file.write(client.ClientGenerator("HammockClient", resources1).code + '\n')
        client_file.flush()
        sys.path.append('build')
        client_class = importlib.import_module("hammock_client").HammockClient
    finally:
        fcntl.flock(client_file.fileno(), fcntl.LOCK_UN)
        client_file.close()
    return client_class(*args, **kwargs)


class TestClient(unittest.TestCase):

    def setUp(self):
        self._client = get_client(url="http://example.com:8080")

    def test_client(self):
        self.assertTrue(hasattr(self._client, "dict"))
        self.assertTrue(hasattr(self._client, "text"))
        self.assertTrue(hasattr(self._client, "headers"))
        self.assertTrue(hasattr(self._client.dict, "insert"))
        self.assertTrue(hasattr(self._client.dict, "get"))
        self.assertTrue(hasattr(self._client.dict, "update"))
        self.assertTrue(hasattr(self._client.dict, "remove"))
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
        self.assertTrue(hasattr(self._client.sub_resource.nested, "additional"))
        self.assertTrue(hasattr(self._client.sub_resource.nested, "additional_2"))

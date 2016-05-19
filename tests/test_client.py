from __future__ import absolute_import
import unittest
import importlib
import os
import sys
import hammock.client as client
import tests.resources1 as resources1


if not os.path.exists('build'):
    os.mkdir('build')
with open('build/hammock_client.py', 'w') as client_file:
    client_file.write(client.ClientGenerator("HammockClient", resources1).code + '\n')


def get_client(*args, **kwargs):
    sys.path.append('build')
    client_class = importlib.import_module("hammock_client").HammockClient
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

    def test_auth_specials(self):
        self.assertTrue(hasattr(self._client, "auth"))
        for method_name in ('login', 'logout', 'refresh'):
            self.assertTrue(hasattr(self._client.auth, method_name))
            self.assertTrue(hasattr(self._client, method_name))
        self.assertTrue(hasattr(self._client.auth, 'status'))
        self.assertFalse(hasattr(self._client.auth, '_status'))

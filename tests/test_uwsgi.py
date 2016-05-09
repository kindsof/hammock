from __future__ import absolute_import
import six
import unittest
import logging
import requests

import hammock.types.file as file_module
import tests.resources1.exceptions as exceptions_resouce
import tests.uwsgi_base as uwsgi_base


class TestUwsgi(uwsgi_base.UwsgiBase):

    @unittest.skipIf(
        six.PY3,
        '''
        Due to a bug in uwsgi with BytesIO under python 3,
        https://github.com/unbit/uwsgi/issues/1126
        '''
    )
    def test_files(self):
        size_mb = 100
        content_length = size_mb << 20

        logging.info("Sending %dmb to server", size_mb)
        file_object = file_module.File(
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
        file_object = file_module.File(six.BytesIO(data), content_length)
        response = self._client.files.echo(file_object)
        response_data = list(response.stream())
        response_data = six.b('').join(response_data)
        self.assertEqual(data, response_data)

    def test_exceptions(self):
        with self.assertRaises(requests.HTTPError) as exc:
            self._client.exceptions.internal()
        self.assertFalse(exc.exception.response.ok)
        self.assertEqual(500, exc.exception.response.status_code)
        self.assertDictEqual(
            {
                'status': 500,
                'title': 'Internal Server Error',
                'description': repr(Exception(exceptions_resouce.DESCRIPTION)),
            },
            exc.exception.response.json()
        )

        with self.assertRaises(requests.HTTPError) as exc:
            self._client.exceptions.not_found()
        self.assertFalse(exc.exception.response.ok)
        self.assertEqual(404, exc.exception.response.status_code)
        self.assertDictEqual(
            {
                'status': 404,
                'title': 'Not Found',
                'description': exceptions_resouce.DESCRIPTION,
            },
            exc.exception.response.json()
        )

    def test_keyword_mapping(self):
        self.assertEqual(self._client.keyword_map.post(valid1='1', valid2='1'), {'valid1': '1', 'valid2': '1'})
        self.assertEqual(self._client.keyword_map.post(valid1=None), {'valid1': None, 'valid2': None})

        self.assertEqual(self._client.keyword_map.get(valid1='1', valid2='1'), {'valid1': '1', 'valid2': '1'})
        self.assertEqual(self._client.keyword_map.get(valid1='None'), {'valid1': None, 'valid2': None})

        self.assertEqual(self._client.keyword_map.post(valid1='1'), {'valid1': '1', 'valid2': None})
        self.assertEqual(self._client.keyword_map.get(valid1='1'), {'valid1': '1', 'valid2': None})

    def test_classes_method_names(self):
        self.assertEqual('modified-in-modified', self._client.different_path.different_sub.get())
        self.assertEqual('moshe', self._client.variable_in_url_1.get('moshe'))
        self.assertEqual('moshe', self._client.variable_in_url_2.get('moshe'))

    def test_client_methods(self):
        self.assertEquals(self._client.client_methods.run(3), 3)
        self.assertEquals(self._client.client_methods.run(3, distance=10), 30)
        self.assertEquals(self._client.client_methods.jump(3), 3)

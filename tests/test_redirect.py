from __future__ import absolute_import

import httplib
import os

import six
from mock import mock

import hammock.common as common
import hammock.testing as testing
import tests.base as base
import tests.resources1.redirect as redirect
from hammock.types import Request
from hammock.types import Response


class TestRedirect(base.TestBase):
    YIELD_BEFORE = mock.MagicMock()
    YIELD_AFTER = mock.MagicMock()

    RESOURCE_PARAMS = {'before': YIELD_BEFORE, 'after': YIELD_AFTER}

    @classmethod
    def setUpClass(cls):
        cls._server = testing.Server(port=redirect.PORT, name='test-redirect')

    @classmethod
    def tearDownClass(cls):
        cls._server.close()

    def test_redirect_get_request(self):  # pylint: disable=invalid-name
        """
        verify that we don't pass the body on GET requests.
        :return:
        """
        method = "GET"
        redirect_path = "/redirect/v3/users?key1=val1&key2=val2"
        headers = {"host": "localhost", common.CONTENT_LENGTH: "0"}
        body = None
        self._exec_request(redirect_path, method, body, headers)

    def test_redirect_post_request_with_json_body(self):  # pylint: disable=invalid-name
        method = "POST"
        redirect_path = "/redirect/v3/users"
        body = {"desc": "sent from test", "method": "POST"}
        headers = {
            common.CONTENT_TYPE: common.TYPE_JSON,
            "host": "127.0.0.1",
        }
        self._exec_request(redirect_path, method, body, headers)

    @staticmethod
    def _get_stream_size(stream):
        stream.seek(0, os.SEEK_END)
        body_length = stream.tell()
        stream.seek(0, os.SEEK_SET)
        return body_length

    def test_redirect_post_request_with_binary_body(self):  # pylint: disable=invalid-name
        method = "POST"
        redirect_path = "/redirect/v3/users?key1=val1&key2=val2"

        with open(__file__, 'rb') as file_object:
            body = file_object.read()
        headers = {
            common.CONTENT_TYPE: common.TYPE_OCTET_STREAM,
            common.CONTENT_LENGTH: str(len(body)),
            "host": "localhost",
        }
        self._exec_request(redirect_path, method, body, headers, binary_response=True)

    def test_redirect_post_request_with_large_binary_body(self):  # pylint: disable=invalid-name
        method = "POST"
        redirect_path = "/redirect/v3/users?key1=val1&key2=val2"
        body_stream = six.moves.StringIO()
        with open(__file__, 'rb') as file_object:
            for _ in range(100):
                content = file_object.read()
                if not isinstance(content, six.string_types):
                    content = content.decode()
                body_stream.write(content)

        headers = {
            common.CONTENT_TYPE: common.TYPE_OCTET_STREAM,
            common.CONTENT_LENGTH: str(TestRedirect._get_stream_size(body_stream)),
            "host": "localhost",
        }
        self._exec_request(redirect_path, method, body_stream.getvalue(), headers, binary_response=True)

    def _exec_request(self, redirect_path, method, body, headers, binary_response=False):
        parsed = six.moves.urllib.parse.urlsplit(redirect_path)
        response = self._simulate(
            url=redirect_path,
            method=method,
            body=body,
            headers=headers,
            binary_response=binary_response,
        )
        if common.CONTENT_TYPE not in headers or headers[common.CONTENT_TYPE] == common.TYPE_JSON:
            self.assertEqual(response["path"], parsed.path[len("/redirect"):])
            self.assertEqual(response["query_string"], parsed.query)
            self.assertEqual(response["method"], method)
            self.assertDictContainsSubset({k.lower(): v.lower() for k, v in six.iteritems(headers) if k.lower() != "host"},
                                          {k.lower(): v.lower() for k, v in six.iteritems(response["headers"]) if k.lower() != "host"},
                                          '{} should be a subset in {}'.format(headers, response["headers"]))
            if body:
                self.assertDictEqual(response["body"], body)
            else:
                self.assertEqual(response["body"], None)
        else:
            if not isinstance(response, six.string_types):
                response = response.decode()
            if not isinstance(body, six.string_types):
                body = body.decode()
            self.assertEqual(response, body)

    def test_redirect_with_resource_conflicts(self):  # pylint: disable=invalid-name
        self.assertEqual(self._simulate('GET', "/redirect/specific"), "specific")
        self.assertEqual(self._simulate('GET', "/redirect/specific/not")["path"], "/specific/not")
        self.assertEqual(self._simulate('GET', "/redirect")["path"], "/")

    def test_passthroughs(self):
        self._simulate('POST', '/redirect/post-passthrough', body={'some_data': 'a'})
        self._simulate('POST', '/redirect/post-passthrough-with-body', body={'some_data': 'a'})
        self._simulate('GET', '/redirect/manipulate-path')

    def test_post_generator(self):
        self.YIELD_BEFORE.reset_mock()
        self.YIELD_AFTER.reset_mock()
        self._simulate('POST', '/redirect/post-generator', body={'some_data': 'a'})
        self.YIELD_BEFORE.assert_called_once_with('a')
        self.assertEqual(self.YIELD_AFTER.call_count, 1)
        self.assertIsInstance(self.YIELD_AFTER.call_args[0][0], Response)

    def test_sink_generator(self):
        self.YIELD_BEFORE.reset_mock()
        self.YIELD_AFTER.reset_mock()
        self._simulate('DELETE', '/redirect/sink-generator')
        self.assertEqual(self.YIELD_BEFORE.call_count, 1)
        self.assertIsInstance(self.YIELD_BEFORE.call_args[0][0], Request)
        self.assertEqual(self.YIELD_AFTER.call_count, 1)
        self.assertIsInstance(self.YIELD_AFTER.call_args[0][0], Response)

    def test_sink_receives_kwargs_properly_when_generator(self):
        resp = self._simulate('GET', '/redirect/sink-generator-with-missing-url-params-kwargs/value1/value2')
        self.assertEqual(resp['status'], httplib.INTERNAL_SERVER_ERROR)
        self.YIELD_BEFORE.reset_mock()
        resp = self._simulate('GET', '/redirect/sink-generator-with-full-url-params-kwargs/value1/value2')
        self.assertNotEqual(resp.get('status'), httplib.INTERNAL_SERVER_ERROR)
        self.YIELD_BEFORE.assert_called_once_with('value1', 'value2')

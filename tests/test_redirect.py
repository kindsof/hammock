from __future__ import absolute_import
import hammock.testing as testing
import tests.base as base
import six
import os
import tests.resources1.redirect as redirect
import hammock.common as common


class TestRedirect(base.TestBase):

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

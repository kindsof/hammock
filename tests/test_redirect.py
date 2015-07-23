import os
import json
import urlparse
import falcon
import falcon.testing as testing
import hammock.resource as resource
import hammock.redirect as redirect
import hammock.testing.server as server

# Find the best implementation available on this platform
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class RedirectExample(redirect.Redirect):
    PATH = "/example"

    def __init__(self, api, dest):
        self.__class__.DEST = dest
        super(RedirectExample, self).__init__(api)


class ResourceUnderRedirect(resource.Resource):
    @resource.get("specific")
    def specific(self):  # pylint: disable=unused-argument
        return "specific"

    @classmethod
    def name(cls):
        return "example"


class TestRedirect(testing.TestBase):
    def setUp(self):
        super(TestRedirect, self).setUp()
        self._server = server.Server()
        self.api = falcon.API()
        ResourceUnderRedirect(self.api, "")
        RedirectExample(self.api, "http://%s:%d" % (
            self._server.host, self._server.port))

    def tearDown(self):
        super(TestRedirect, self).tearDown()
        self._server.close()

    def test_redirect_get_request(self):
        """
        verify that we don't pass the body on GET requests.
        :return:
        """
        method = "GET"
        redirect_path = "{}{}".format(RedirectExample.PATH, '/v3/users?key1=val1&key2=val2')
        headers = {"host": "localhost", "content-length": "0"}
        body = None
        self._exec_request(redirect_path, method, body, headers)

    def test_redirect_post_request_with_json_body(self):
        method = "POST"
        redirect_path = "{}{}".format(RedirectExample.PATH, '/v3/users')
        body = json.dumps({"desc": "sent from test", "method": "POST"})
        headers = {"content-type": "application/json",
                   "host": "127.0.0.1",
                   "content-length": str(len(body))}
        self._exec_request(redirect_path, method, body, headers)

    @staticmethod
    def _getStreamSize(stream):
        stream.seek(0, os.SEEK_END)
        body_length = stream.tell()
        stream.seek(0, os.SEEK_SET)
        return body_length

    def test_redirect_post_request_with_binary_body(self):
        method = "POST"
        redirect_path = "{}{}".format(RedirectExample.PATH, '/v3/users?key1=val1&key2=val2')

        with open(__file__, 'rb') as fd:
            body = fd.read()
        headers = {"content-type": "application/octet-stream",
                   "host": "localhost",
                   "content-length": str(len(body))}
        self._exec_request(redirect_path, method, body, headers)

    def test_redirect_post_request_with_large_binary_body(self):
        method = "POST"
        redirect_path = "{}{}".format(RedirectExample.PATH, '/v3/users?key1=val1&key2=val2')

        # Initialize a read buffer

        body_stream = StringIO()
        with open(__file__, 'rb') as fd:
            for _ in range(100):
                body_stream.write(fd.read())

        headers = {"content-type": "application/octet-stream",
                   "host": "localhost",
                   "content-length": str(TestRedirect._getStreamSize(body_stream))}
        self._exec_request(redirect_path, method, body_stream.getvalue(), headers)

    def _exec_request(self, redirect_path, method, body, headers):
        # url = urlparse.urlunsplit(('', '', redirect_path, query_string, ''))
        parsed = urlparse.urlsplit(redirect_path)
        response = self._simulate(
            url=redirect_path,
            method=method,
            body=body,
            headers=headers,
        )
        if "content-type" not in headers or headers["content-type"] == "application/json":
            response = json.loads(response)
            self.assertEqual(response["path"], parsed.path[len(RedirectExample.PATH):])
            self.assertEqual(response["query_string"], parsed.query)
            self.assertEqual(response["method"], method)
            self.assertDictContainsSubset({k: v for k, v in headers.iteritems() if k.lower() != "host"},
                                          {k: v for k, v in response["headers"].iteritems() if k.lower() != "host"},
                                          '{} should be a subset in {}'.format(headers, response["headers"]))
            if body:
                self.assertDictEqual(json.loads(response["body"]), json.loads(body))
            else:
                self.assertEqual(response["body"], None)
        else:
            self.assertEqual(response, body)

    def test_redirect_with_resource_conflicts(self):
        self.assertEqual(json.loads(self._simulate("/example/specific")), "specific")
        self.assertEqual(json.loads(self._simulate("/example/specific/not"))["path"], "/specific/not")
        self.assertEqual(json.loads(self._simulate("/example/"))["path"], "/")

    def _simulate(self, url, method="GET", body=None, headers=None):
        response = self.simulate_request(
            url, method=method, body=body, headers=headers
        )
        if type(response) is not list:
            response = list(response)
        return response[0]


if __name__ == '__main__':
    import unittest

    unittest.main()

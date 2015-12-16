from __future__ import absolute_import
import collections
import falcon
import falcon.testing as testing
import hammock
import hammock.common as common
import hammock.types as types
import tests.resources as resources
import json
import six


def default_404(req, res):  # pylint: disable=unused-argument
    raise falcon.HTTPError(falcon.HTTP_404, "404")


class TestBase(testing.TestBase):

    def before(self):
        self.api.add_sink(default_404)
        hammock.Hammock(self.api, resources)

    def _simulate(self, method, url, query_string=None, body=None, headers=None, binary_response=False):
        kwargs = {}
        headers = headers or {}
        if query_string:
            kwargs["query_string"] = query_string
        if body:
            content_type = headers.get(common.CONTENT_TYPE, common.TYPE_JSON)
            kwargs["body"] = json.dumps(body) if content_type == common.TYPE_JSON else body
            headers.update({common.CONTENT_TYPE: content_type})
        kwargs["headers"] = headers
        response = self.simulate_request(url, method=method, **kwargs)
        result = six.b('').join(response) if isinstance(response, collections.Iterable) else response
        if not binary_response:
            result = result.decode()
        headers = types.Headers(dict(self.srmock.headers))
        if not binary_response and common.TYPE_JSON in headers.get(common.CONTENT_TYPE, common.TYPE_JSON):
            result = json.loads(result)
        return result

    def assert_status(self, status, *args, **kwargs):
        response = self._simulate(*args, **kwargs)
        self.assertIn(str(status), self.srmock.status)
        return response

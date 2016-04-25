from __future__ import absolute_import
import collections
import falcon
import falcon.testing as testing
try:
    import ujson as json
except ImportError:
    import json
import six
import importlib
import hammock
import hammock.common as common
import hammock.types as types


def default_404(req, res):  # pylint: disable=unused-argument
    raise falcon.HTTPError(falcon.HTTP_404, "404")


class TestBase(testing.TestBase):

    RESOURCES = 'tests.resources'
    RESOURCE_PARAMS = {}
    POLICY = None
    CREDENTIAL_CLASS = None

    def before(self):
        self.api.add_sink(default_404)
        resources = importlib.import_module(self.RESOURCES)
        hammock.Hammock(self.api, resources, policy_file=self.POLICY, credentials_class=self.CREDENTIAL_CLASS, **self.RESOURCE_PARAMS)

    def _simulate(self, method, url, query_string=None, body=None, headers=None, binary_response=False):
        kwargs = {}
        headers = headers or {}
        if query_string:
            kwargs["query_string"] = query_string
        if body is not None:
            content_type = headers.get(common.CONTENT_TYPE, common.TYPE_JSON)
            kwargs["body"] = json.dumps(body) if common.TYPE_JSON in content_type else body
            headers.update({common.CONTENT_TYPE: content_type})
        kwargs["headers"] = headers
        response = self.simulate_request(url, method=method, **kwargs)
        if isinstance(response, collections.Iterable):
            result = six.b('').join(response)
        else:
            result = response
        if not binary_response:
            result = result.decode(common.ENCODING)
        headers = types.Headers(dict(self.srmock.headers))
        if not binary_response and common.TYPE_JSON in headers.get(common.CONTENT_TYPE, ''):
            result = json.loads(result)
        return result

    def assert_status(self, status, *args, **kwargs):
        response = self._simulate(*args, **kwargs)
        if str(status) not in self.srmock.status:
            raise AssertionError("Got bad status {} (expected {}) reason: {}".format(self.srmock.status, status, response))
        return response

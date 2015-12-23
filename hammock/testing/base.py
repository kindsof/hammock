from __future__ import absolute_import
import os
import collections
import json
import six
import importlib
import hammock
import hammock.common as common
import hammock.types as types
import hammock.exceptions as exceptions


def default_404(req, res):  # pylint: disable=unused-argument
    raise exceptions.NotFound()


if os.environ.get('BACKEND') == 'falcon':
    import falcon.testing as testing
    Base = testing.TestBase
elif os.environ.get('BACKEND') == 'aiohttp':
    if not six.PY3:
        raise RuntimeError('For aiohttp, must use python >= 3.5')
    from . import aweb
    Base = aweb.AWebTest
else:
    raise RuntimeError('Must specify backend library')


class TestBase(Base):

    RESOURCES = 'tests.resources'
    hammock = None

    def before(self, **kwargs):
        # self.api.add_sink(default_404)
        resources = importlib.import_module(self.RESOURCES)
        self.hammock = hammock.Hammock(os.environ.get('BACKEND'), resources, **kwargs)
        self.api = self.hammock.api

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

        # Run backend depended simulate request method
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
        self.assertIn(str(status), self.srmock.status)
        return response

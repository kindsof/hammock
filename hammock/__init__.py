from __future__ import absolute_import
import hammock.backends as backends
import hammock.resource_node as resource_node
import hammock.wrappers as wrappers
from hammock.common import CONTENT_TYPE, CONTENT_LENGTH   # noqa  # pylint: disable=unused-import
from hammock.common import TYPE_JSON, TYPE_OCTET_STREAM, TOKEN_ENTRY, KW_HEADERS   # noqa  # pylint: disable=unused-import
from hammock.resource import Resource  # noqa  # pylint: disable=unused-import


class Hammock(resource_node.ResourceNode):
    def __init__(self, api, resource_package, **resource_params):
        self._api = api
        self._backend = backends.get(api)
        self._backend.add_resources(self, resource_package, **resource_params)


def get(path='', **kwargs):
    return wrappers.wrapper(path, 'GET', **kwargs)


def head(path='', **kwargs):
    return wrappers.wrapper(path, 'HEAD', **kwargs)


def post(path='', **kwargs):
    return wrappers.wrapper(path, 'POST', **kwargs)


def put(path='', **kwargs):
    return wrappers.wrapper(path, 'PUT', **kwargs)


def delete(path='', **kwargs):
    return wrappers.wrapper(path, 'DELETE', **kwargs)


def patch(path='', **kwargs):
    return wrappers.wrapper(path, 'PATCH', **kwargs)


def get_passthrough(dest, path='', **kwargs):
    return wrappers.wrapper(path, 'GET', dest=dest, **kwargs)


def post_passthrough(dest, path='', **kwargs):
    return wrappers.wrapper(path, 'POST', dest=dest, **kwargs)


def put_passthrough(dest, path='', **kwargs):
    return wrappers.wrapper(path, 'PUT', dest=dest, **kwargs)


def delete_passthrough(dest, path='', **kwargs):
    return wrappers.wrapper(path, 'DELETE', dest=dest, **kwargs)


def sink(path='', **kwargs):
    return wrappers.wrapper(path, 'SINK', **kwargs)

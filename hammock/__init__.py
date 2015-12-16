from __future__ import absolute_import
import hammock.resource_node as resource_node
import hammock.backends as backends
import hammock.sink as sink_module
import hammock.route as route
from hammock.resource import Resource  # noqa  # pylint: disable=unused-import
from hammock.common import TYPE_JSON, TYPE_OCTET_STREAM, TOKEN_ENTRY, KW_HEADERS   # noqa  # pylint: disable=unused-import
from hammock.common import CONTENT_TYPE, CONTENT_LENGTH   # noqa  # pylint: disable=unused-import


class Hammock(resource_node.ResourceNode):
    def __init__(self, api, resource_package):
        self._api = api
        self._backend = None
        if backends.falcon and isinstance(api, backends.falcon.API):
            self._backend = backends.Falcon(api)
        elif backends.aweb and isinstance(api, backends.aweb.Application):
            self._backend = backends.AWeb(api)
        self._backend.add_resources(self, resource_package)


def get(path="", **kwargs):
    return route.route(path, "GET", **kwargs)


def head(path="", **kwargs):
    return route.route(path, "HEAD", **kwargs)


def post(path="", **kwargs):
    return route.route(path, "POST", **kwargs)


def put(path="", **kwargs):
    return route.route(path, "PUT", **kwargs)


def delete(path="", **kwargs):
    return route.route(path, "DELETE", **kwargs)


def patch(path="", **kwargs):
    return route.route(path, "PATCH", **kwargs)


def get_passthrough(dest, path="", **kwargs):
    return route.passthrough(path, "GET", dest=dest, **kwargs)


def post_passthrough(dest, path="", **kwargs):
    return route.passthrough(path, "POST", dest=dest, **kwargs)


def put_passthrough(dest, path="", **kwargs):
    return route.passthrough(path, "PUT", dest=dest, **kwargs)


def delete_passthrough(dest, path="", **kwargs):
    return route.passthrough(path, "DELETE", dest=dest, **kwargs)


def sink(path="", **kwargs):
    return sink_module.sink(path=path, **kwargs)

from __future__ import absolute_import
import six
import hammock.route as route
import hammock.sink as _sink
import hammock.common as common
import hammock.exceptions as exceptions
import collections
import logging
import functools
import re

TOKEN_ENTRY = common.TOKEN_ENTRY
CONTENT_TYPE = common.CONTENT_TYPE
TYPE_JSON = common.TYPE_JSON
TYPE_OCTET_STREAM = common.TYPE_OCTET_STREAM
KW_HEADERS = common.KW_HEADERS
CONVERT_PATH_VARIABLES = functools.partial(re.compile(r'{([a-zA-Z][a-zA-Z_]*)}').sub, r'(?P<\1>[^/]+)')


class Resource(object):

    def __init__(self, api, base_path):
        self._api = api
        self._base_path = base_path
        self._add_route_methods(base_path)
        self._add_sink_methods(base_path)
        self._default_exception_handler = getattr(self, "DEFAULT_EXCEPTION_HANDLER", None)

    def _add_route_methods(self, base_path):
        paths = collections.defaultdict(dict)
        for method in route.iter_route_methods(self):
            paths[method.path]["on_%s" % method.method.lower()] = functools.partial(method.responder, self)
        for path, methods in six.iteritems(paths):
            new_route = type(
                "_".join([
                    "Resource",
                    base_path.replace("/", "_"),
                    self.name().capitalize(),
                    common.PATH_TO_NAME(path),
                    ]),
                (), methods)()
            full_path = "/%s" % common.url_join(base_path, self.name(), path)
            self._api.add_route(full_path, new_route)
            logging.debug("Added route %s", full_path)

    def _add_sink_methods(self, base_path):
        sinks = {}
        for method in _sink.iter_sink_methods(self):
            full_path = "/" + common.url_join(base_path, self.name(), method.path)
            pattern = re.compile(CONVERT_PATH_VARIABLES(full_path))
            sinks[pattern] = method.method
        for pattern in sorted(sinks, key=functools.cmp_to_key(lambda p1, p2: len(p1.pattern) - len(p2.pattern))):
            self._api.add_sink(functools.partial(sinks[pattern], self), pattern)
            logging.debug("Added sink %s for %s", pattern.pattern, repr(sinks[pattern].__code__))

    @classmethod
    def name(cls):
        return getattr(cls, "PATH", cls.__name__.lower())

    def handle_exception(self, exc, exception_handler):
        if exception_handler:
            exc = exception_handler(exc)
        elif self._default_exception_handler:
            exc = self._default_exception_handler(exc)
        raise self._convert_to_internal_server_error(exc)

    @staticmethod
    def _convert_to_internal_server_error(exc):
        return exc if isinstance(exc, exceptions.HttpError) else exceptions.InternalServerError(str(exc))


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


def passthrough(dest, path="", **kwargs):
    return _sink.sink(path, dest=dest, **kwargs)


def sink(path="", **kwargs):
    return _sink.sink(path=path, **kwargs)

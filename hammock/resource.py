import hammock.route as route
import hammock.sink as _sink
import hammock.common as common
import collections
import logging
import functools
import re


TOKEN_ENTRY = "X-Auth-Token"
CONTENT_TYPE = route.CONTENT_TYPE
TYPE_JSON = route.TYPE_JSON
TYPE_OCTET_STREAM = route.TYPE_OCTET_STREAM
KW_HEADERS = route.KW_HEADERS
EXPRESSION_PATTERN = r'{([a-zA-Z][a-zA-Z_]*)}'


class Resource(object):

    def __init__(self, api, base_path):
        self._api = api
        self._add_route_methods(base_path)
        self._add_sink_methods(base_path)

    def _add_route_methods(self, base_path):
        paths = collections.defaultdict(dict)
        for method in route.iter_route_methods(self):
            paths[method.path]["on_%s" % method.method.lower()] = functools.partial(method.responder, self)
        for path, methods in paths.iteritems():
            new_route = type(
                "_".join([
                    "Resource",
                    base_path.replace("/", "_"),
                    self.name().capitalize(),
                    path.translate(None, "{}/."),
                    ]),
                (), methods)()
            full_path = "/%s" % common.url_join(base_path, self.name(), path)
            self._api.add_route(full_path, new_route)
            logging.debug("Added route %s", full_path)

    def _add_sink_methods(self, base_path):
        sinks = {}
        for method in _sink.iter_sink_methods(self):
            full_path = "/" + common.url_join(base_path, self.name(), method.path)
            pattern = re.compile(re.sub(EXPRESSION_PATTERN, r'(?P<\1>[^/]+)', full_path))
            sinks[pattern] = method.method
        for pattern in sorted(sinks, cmp=lambda p1, p2: len(p1.pattern) - len(p2.pattern)):
            self._api.add_sink(sinks[pattern], pattern)
            logging.info("Added sink %s", full_path)

    @classmethod
    def name(cls):
        return getattr(cls, "PATH", cls.__name__.lower())


def get(path="", **kwargs):
    return route.route(path, "GET", **kwargs)


def post(path="", **kwargs):
    return route.route(path, "POST", **kwargs)


def put(path="", **kwargs):
    return route.route(path, "PUT", **kwargs)


def delete(path="", **kwargs):
    return route.route(path, "DELETE", **kwargs)


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

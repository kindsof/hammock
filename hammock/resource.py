import hammock.decorator as decorator
import hammock.common as common
import collections
import logging
import functools


TOKEN_ENTRY = "X-Auth-Token"
CONTENT_TYPE = decorator.CONTENT_TYPE
TYPE_JSON = decorator.TYPE_JSON
TYPE_OCTET_STREAM = decorator.TYPE_OCTET_STREAM
KW_HEADERS = decorator.KW_HEADERS


class Resource(object):

    def __init__(self, api, base_path):
        self._api = api
        paths = collections.defaultdict(dict)
        for method in decorator.iter_route_methods(self):
            paths[method.path]["on_%s" % method.method.lower()] = functools.partial(method.responder, self)
        for path, methods in paths.iteritems():
            route = type(
                "_".join([
                    "Resource",
                    base_path.replace("/", "_"),
                    self.name().capitalize(),
                    path.translate(None, "{}/."),
                    ]),
                (), methods)()
            api.add_route("/%s" % common.url_join(base_path, self.name(), path), route)
        logging.debug("Added %s to api", self.name())

    @classmethod
    def name(cls):
        return cls.__name__.lower()


def get(path="", **kwargs):
    return decorator.route(path, "GET", **kwargs)


def post(path="", **kwargs):
    return decorator.route(path, "POST", **kwargs)


def put(path="", **kwargs):
    return decorator.route(path, "PUT", **kwargs)


def delete(path="", **kwargs):
    return decorator.route(path, "DELETE", **kwargs)

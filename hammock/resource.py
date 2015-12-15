from __future__ import absolute_import
import hammock.sink as sink_module
import hammock.route as route
import hammock.common as common
import hammock.exceptions as exceptions

TOKEN_ENTRY = common.TOKEN_ENTRY
CONTENT_TYPE = common.CONTENT_TYPE
TYPE_JSON = common.TYPE_JSON
TYPE_OCTET_STREAM = common.TYPE_OCTET_STREAM
KW_HEADERS = common.KW_HEADERS


class Resource(object):

    def __init__(self):
        self._default_exception_handler = getattr(self, "DEFAULT_EXCEPTION_HANDLER", None)

    @classmethod
    def name(cls):
        return getattr(cls, "PATH", cls.__name__.lower())

    def handle_exception(self, exc, exception_handler):
        if exception_handler:
            exc = exception_handler(exc)
        elif self._default_exception_handler:
            exc = self._default_exception_handler(exc)
        raise self._to_internal_server_error(exc)

    @staticmethod
    def _to_internal_server_error(exc):
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
    return sink_module.sink(path, dest=dest, **kwargs)


def sink(path="", **kwargs):
    return sink_module.sink(path=path, **kwargs)

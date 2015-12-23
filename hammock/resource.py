from __future__ import absolute_import
import logging
import collections
import functools
import hammock.exceptions as exceptions
import hammock.common as common
import hammock.wrappers.wrapper as route_base
import hammock.wrappers as _routes


LOG = logging.getLogger(__name__)


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

    @property
    def routes(self):
        """
        :return: A dict representing routes in a resource: { url: {method: responder} }
        """
        routes = collections.defaultdict(dict)
        for route_method in self.iter_route_methods():
            method = route_method.method.upper()
            routes[common.url_join(self.name(), route_method.path)][method] = functools.partial(route_method, self)
        return routes

    @property
    def sinks(self):
        """
        :return: A list representing sinks in a resource: ( url, responder )
            The list is sorted by url size, largest first.
        """
        return [
            (common.url_join(self.name(), sink.path), functools.partial(sink.responder, self))
            for sink in self.iter_sink_methods()
        ]

    @staticmethod
    def _to_internal_server_error(exc):
        if isinstance(exc, exceptions.HttpError):
            return exc
        else:
            LOG.exception('Internal server Error')
            return exceptions.InternalServerError(str(exc))

    @classmethod
    def iter_route_methods(cls, route_class=route_base.Wrapper):
        return (
            getattr(cls, attr) for attr in dir(cls)
            if isinstance(getattr(cls, attr, None), route_class)
        )

    @classmethod
    def iter_sink_methods(cls):
        return (
            getattr(cls, attr) for attr in dir(cls)
            if getattr(getattr(cls, attr, None), 'is_sink', False)
        )

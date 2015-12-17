from __future__ import absolute_import
import collections
import functools
import hammock.exceptions as exceptions
import hammock.common as common


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
            routes[common.url_join(self.name(), route_method.path)][method] = route_method.responder
        return routes

    @property
    def sinks(self):
        """
        :return: A list representing sinks in a resource: ( url, responder )
            The list is sorted by url size, largest first.
        """
        return [
            (common.url_join(self.name(), sink.path), sink.responder)
            for sink in self.iter_sink_methods()
        ]

    @staticmethod
    def _to_internal_server_error(exc):
        return exc if isinstance(exc, exceptions.HttpError) else exceptions.InternalServerError(str(exc))

    @classmethod
    def iter_route_methods(cls):
        return (
            getattr(cls, attr) for attr in dir(cls)
            if getattr(getattr(cls, attr), 'is_route', False)
        )

    @classmethod
    def iter_sink_methods(cls):
        return sorted(
            (
                getattr(cls, attr) for attr in dir(cls)
                if getattr(getattr(cls, attr), 'is_sink', False)
            ),
            key=functools.cmp_to_key(lambda p1, p2: len(p1.pattern) - len(p2.pattern))
        )

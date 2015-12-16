from __future__ import absolute_import
import hammock.exceptions as exceptions


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

from __future__ import absolute_import
import logging
import abc
from hammock import exceptions
from hammock.types import func_spec
import hammock.common as common

# XXX: temporary workaround,
# until all dependencies will change their exceptions to hammock.exceptions.
try:
    import falcon
except ImportError:
    # fake falcon module and some specific exception, so we can except it later.
    falcon = type('falcon', (object,), {'HTTPError': type('HTTPError', (Exception,), {})})  # pylint: disable=invalid-name
# XXX


LOG = logging.getLogger(__name__)


class Wrapper(object):
    """
    A class that wraps a function,
    used to decorate route and sink methods in a resource class
    """

    def __init__(
        self, func, path,
        exception_handler=None,
        dest=None, pre_process=None, post_process=None, trim_prefix=False
    ):
        """
        Create a decorator of a method in a resource class
        :param func: a function to decorate
        :param path: url path of the function
        :param exception_handler: a specific handler for exceptions.
        :param dest: a hostname + path to pass the request to.
        :param pre_process: a method to invoke on the request before process.
        :param post_process:  a method to invoke on the request after process.
        :param trim_prefix: a prefix to trim from the path.
        :return: the func, decorated
        """
        self.func = func
        self.spec = func_spec.FuncSpec(func)
        self._resource = None  # Can be determined only after resource class instantiation.
        self.path = path
        self.exception_handler = exception_handler
        self.dest = dest
        self.pre_process = pre_process
        self.post_process = post_process
        self.trim_prefix = trim_prefix

        self.__name__ = func.__name__
        self.__doc__ = func.__doc__

        # If it is a proxy, make sure function doesn't do anything.
        if self.dest is not None:
            common.func_is_pass(func)

    def __call__(self, *args, **kwargs):
        """
        The actual method that decorate the wrapped function.
        """
        return self.func(self._resource, *args, **kwargs)

    def set_resource(self, resource):
        self._resource = resource

    def call(self, req):
        """
        Calls self.func with resource and req parameters.
        Wraps it with error handling.
        :param req: a hammock.types.request.Request object.
        :return: response as hammock.types.response.Response object.
        """
        context = {}
        try:
            if self.trim_prefix:
                req.trim_prefix(self.trim_prefix)
            if self.pre_process:
                self.pre_process(req, context, **req.url_params)  # pylint: disable=not-callable

            resp = self._wrapper(req)

            if self.post_process:
                resp = self.post_process(resp, context, **req.url_params)  # pylint: disable=not-callable

        except exceptions.HttpError as exc:
            common.log_exception(exc, req.uid)
            raise
        # XXX: temporary, until all dependencies will transfer to hammock exceptions
        except falcon.HTTPError as exc:
            self._exc_log_and_handle(exc, req)
        # XXX
        except Exception as exc:  # pylint: disable=broad-except
            self._exc_log_and_handle(exc, req)
        else:
            LOG.debug('[response %s] status: %s, content: %s', req.uid, resp.status, resp.content)
            return resp

    def _exc_log_and_handle(self, exc, req):
        self._resource.handle_exception(exc, self.exception_handler, req.uid)

    @abc.abstractmethod
    def _wrapper(self, req):
        """
        :param req: a hammock.types.request.Request object.
        :return: response as hammock.types.response.Response object.
        """

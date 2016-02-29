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

    path = None
    method = None
    exception_handler = None
    dest = None
    rule_name = 'default'
    pre_process = None
    post_process = None
    trim_prefix = False

    def __init__(self, func):
        """
        Create a decorator of a method in a resource class
        :param func: a function to decorate
        :return: a decorator
        """
        # decorator.decorate(func, self)
        self.spec = func_spec.FuncSpec(func)
        self.func = func
        self._resource = None  # Can be determined only after resource class instantiation.
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__

        # If it is a proxy, make sure function doesn't do anything.
        if self.dest is not None:
            common.func_is_pass(func)

    def set_resource(self, resource):
        self._resource = resource

    def __call__(self, *args, **kwargs):
        return self.func(self._resource, *args, **kwargs)

    def _exc_log_and_handle(self, exc, req):
        self._resource.handle_exception(exc, self.exception_handler)
        common.log_exception(exc, req.uid)

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
            if self.__class__.pre_process:
                self.__class__.pre_process(req, context, **req.url_params)  # pylint: disable=not-callable

            resp = self._wrapper(req)

            if self.__class__.post_process:
                resp = self.__class__.post_process(resp, context, **req.url_params)  # pylint: disable=not-callable

        except exceptions.HttpError as exc:
            self._exc_log_and_handle(exc, req)
        # XXX: temporary, until all dependencies will transfer to hammock exceptions
        except falcon.HTTPError as exc:
            self._exc_log_and_handle(exc, req)
        # XXX
        except Exception as exc:  # pylint: disable=broad-except
            self._exc_log_and_handle(exc, req)
        else:
            LOG.debug('[response %s] status: %s, content: %s', req.uid, resp.status, resp.content)
            return resp

    @abc.abstractmethod
    def _wrapper(self, req):
        """
        :param req: a hammock.types.request.Request object.
        :return: response as hammock.types.response.Response object.
        """

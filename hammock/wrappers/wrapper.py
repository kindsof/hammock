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

    def __init__(self, func):
        """
        Create a decorator
        :param func: a function to decorate
        :return: a decorator
        """
        # decorator.decorate(func, self)
        self.spec = func_spec.FuncSpec(func)
        self.func = func
        self.__name__ = self.func.__name__
        self.__doc__ = self.func.__doc__

    def __call__(self, resource, req):
        """
        Calls self.func with resource and req parameters.
        Wraps it with error handling.
        :param req: a hammock.types.request.Request object.
        :return: response as hammock.types.response.Response object.
        """
        try:
            resp = self._wrapper(resource, req)
        except exceptions.HttpError:
            raise
        # XXX: temporary, until all dependencies will transfer to hammock exceptions
        except falcon.HTTPError:
            raise
        # XXX
        except Exception as exc:  # pylint: disable=broad-except
            common.log_exception(exc, req.uid)
            resource.handle_exception(exc, self.exception_handler)
        else:
            LOG.debug('[response %s] status: %s, content: %s', req.uid, resp.status, resp.content)
            return resp

    @abc.abstractmethod
    def _wrapper(self, resource, req):
        """
        :param req: a hammock.types.request.Request object.
        :return: response as hammock.types.response.Response object.
        """

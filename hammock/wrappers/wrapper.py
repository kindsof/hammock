from __future__ import absolute_import
import logging
import abc
from hammock.types import func_spec
import hammock.common as common
from py_zipkin import zipkin
from py_zipkin.zipkin import zipkin_span
import requests
import string
import random


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

            req.update_content_length()

            def http_transport(encoded_span):
                # The collector expects a thrift-encoded list of spans. Instead of
                # decoding and re-encoding the already thrift-encoded message, we can just
                # add header bytes that specify that what follows is a list of length 1.
                body = '\x0c\x00\x00\x00\x01' + encoded_span
                requests.post(
                    'http://localhost:9411/api/v1/spans',
                    data=body,
                    headers={'Content-Type': 'application/x-thrift'},
                )

            def _gen_random_id():
                return ''.join(random.choice(string.digits) for i in range(16))

            # import pytest; pytest.set_trace()
            headers = req.headers
            trace_id = headers.get('X-B3-TraceId') or _gen_random_id()
            parent_span_id = headers.get('X-B3-ParentSpanId')
            is_sampled = str(headers.get('X-B3-Sampled') or '1') == '1'  # changed from flask_zipkin
            flags = headers.get('X-B3-Flags')

            zipkin_attrs = zipkin.ZipkinAttrs(
                trace_id=trace_id,
                span_id=_gen_random_id(),
                parent_span_id=parent_span_id,
                flags=flags,
                is_sampled=is_sampled,
            )
            resource_package = self._resource.params["_resource_package"].__name__
            top_resource_package = resource_package.split('.')[0]
            with zipkin_span(
                    service_name=top_resource_package,
                    span_name=resource_package + ':' + self.func.__name__,
                    transport_handler=http_transport,
                    port=42,
                    sample_rate=100.0,  # Value between 0.0 and 100.0
                    zipkin_attrs=zipkin_attrs):
                resp = self._wrapper(req)
            # import pytest; pytest.set_trace()

            resp.update_content_length()

            if self.post_process:
                self.post_process(resp, context, **req.url_params)  # pylint: disable=not-callable

            resp.update_content_length()

        except Exception as exc:  # pylint: disable=broad-except
            self._resource.handle_exception(exc, self.exception_handler, req.uid)
        else:
            LOG.debug('[response %s] status: %s, content: %s', req.uid, resp.status, resp.content)
            return resp

    @property
    def params(self):
        return self._resource.params

    @property
    def policy(self):
        return self.params.get('_policy')

    @property
    def credentials_class(self):
        return self.params.get('_credentials_class')

    @abc.abstractmethod
    def _wrapper(self, req):
        """
        :param req: a hammock.types.request.Request object.
        :return: response as hammock.types.response.Response object.
        """

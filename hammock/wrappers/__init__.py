from __future__ import absolute_import
from .route import Route
from .sink import Sink
import hammock.common as common


def is_sink(method):
    return method.upper() == 'SINK'


def wrapper(
    path, method,
    success_code=200,
    dest=None,
    pre_process=None,
    post_process=None,
    trim_prefix=False,
    client_methods=None,
    exception_handler=None,
    response_content_type=common.TYPE_JSON,
):
    """
    :param path: relative path for route
    :param method: HTTP method,
        if 'SINK', all methods will be accepted, with a prefix equal to path.
    :param client_methods: a dict of how the method will look like in client code,
        and overriding keys - values for method parameters.
        { method-name: { key: value }}
    :param success_code: a code to return in http response.
    :param dest: a hostname + path to pass the request to.
    :param pre_process: a method to invoke on the request before process.
    :param post_process:  a method to invoke on the request after process.
    :param trim_prefix: a prefix to trim from the path.
    :param response_content_type: content type of response.
    :param exception_handler: a specific handler for exceptions.
    :return: a decorator for a route method.
    """
    name = ''.join(part.capitalize() for part in [method.upper(), common.PATH_TO_NAME(path)])
    overrides = dict(
        path=path,
        dest=dest,
        pre_process=staticmethod(pre_process),
        post_process=staticmethod(post_process),
        trim_prefix=trim_prefix,
        exception_handler=staticmethod(exception_handler),
        client_methods=client_methods,
        success_code=Route.get_status_code(success_code),
        response_content_type=response_content_type,  # XXX: This should be removed.
    )
    if not is_sink(method):
        overrides['method'] = method.upper()
    wrapper_type = Route if not is_sink(method) else Sink
    return type(name, (wrapper_type, ), overrides)

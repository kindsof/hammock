from __future__ import absolute_import
from .route import Route
from .passthrough import Passthrough
import hammock.common as common


def route(path, method, success_code=200, client_methods=None, exception_handler=None, response_content_type=common.TYPE_JSON):
    """
    :param path: relative path for route
    :param method: HTTP method
    :param client_methods: a dict of how the method will look like in client code,
        and overriding keys - values for method parameters.
        { method-name: { key: value }}
    :param success_code: a code to return in http response.
    :param response_content_type: content type of response.
    :param exception_handler: a specific handler for exceptions.
    :return: a decorator for a route method.
    """
    name = ''.join(part.capitalize() for part in ['Route', common.PATH_TO_NAME(path), method])
    return type(
        name,
        (Route, ),
        dict(
            path=path,
            method=method.upper(),
            exception_handler=exception_handler,
            client_methods=client_methods,
            success_code=Route.get_status_code(success_code),
            response_content_type=response_content_type,  # XXX: This should be removed.
        ),
    )


def passthrough(path, method, dest, pre_process=None, post_process=None, trim_prefix=False, exception_handler=None):
    return type(
        ''.join(part.capitalize() for part in ['Passthrough', common.PATH_TO_NAME(path), method]),
        (Passthrough, ),
        dict(
            path=path,
            method=method.upper(),
            dest=dest,
            exception_handler=exception_handler,
            pre_process=staticmethod(pre_process),
            post_process=staticmethod(post_process),
            trim_prefix=trim_prefix,
        ),
    )

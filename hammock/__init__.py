from __future__ import absolute_import

from hammock.backends import _falcon as falcon
from hammock.common import *   # noqa  # pylint: disable=unused-import
from hammock.resource import Resource  # noqa  # pylint: disable=unused-import
from hammock.wrappers import sink as _sink

try:
    from hammock.backends import aweb
except SyntaxError:
    import munch
    aweb = munch.Munch(aweb=None)
from . import wrappers as wrappers


def Hammock(backend, resource_package, **kwargs):  # noqa  # pylint: disable=invalid-name
    """
    Get an Hammock instance
    :param backend: which api to use, falcon or aiohttp
    :param kwargs: kwargs to pass to the initiation of the api
    :return: an Hammock instance.
    """

    if not backend or backend not in {'falcon', 'aiohttp'}:
        raise RuntimeError("Invalid Backend given, '{}'".format(backend))
    if falcon.falcon and backend == 'falcon':
        return falcon.Falcon(resource_package, **kwargs)
    elif aweb.aweb and backend == 'aiohttp':
        return aweb.AWeb(resource_package, **kwargs)
    else:
        raise RuntimeError("Requested backend library '{}' not available.".format(backend))


def get(path='', **kwargs):
    return wrappers.route(path, 'GET', **kwargs)


def head(path='', **kwargs):
    return wrappers.route(path, 'HEAD', **kwargs)


def post(path='', **kwargs):
    return wrappers.route(path, 'POST', **kwargs)


def put(path='', **kwargs):
    return wrappers.route(path, 'PUT', **kwargs)


def delete(path='', **kwargs):
    return wrappers.route(path, 'DELETE', **kwargs)


def patch(path='', **kwargs):
    return wrappers.route(path, 'PATCH', **kwargs)


def get_passthrough(dest, path='', **kwargs):
    return wrappers.passthrough(path, 'GET', dest=dest, **kwargs)


def post_passthrough(dest, path='', **kwargs):
    return wrappers.passthrough(path, 'POST', dest=dest, **kwargs)


def put_passthrough(dest, path='', **kwargs):
    return wrappers.passthrough(path, 'PUT', dest=dest, **kwargs)


def delete_passthrough(dest, path='', **kwargs):
    return wrappers.passthrough(path, 'DELETE', dest=dest, **kwargs)


def sink(path='', **kwargs):
    return _sink.sink(path=path, **kwargs)

# __all__ = (
#     'Hammock',
#     'Resource',
#     'get', 'get_passthrough',
#     'post', 'post_passthrough',
#     'put', 'put_passthrough',
#     'delete', 'delete_passthrough',
#     'head',
#     'sink',
#     'CONTENT_TYPE', 'CONTENT_LENGTH', 'TYPE_JSON', 'TYPE_OCTET_STREAM', 'TOKEN_ENTRY', 'KW_HEADERS',
# )

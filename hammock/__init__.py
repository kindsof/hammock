from __future__ import absolute_import
import warnings
import hammock.wrappers as wrappers
from hammock.common import CONTENT_TYPE, CONTENT_LENGTH   # noqa  # pylint: disable=unused-import
from hammock.common import TYPE_JSON, TYPE_OCTET_STREAM, TOKEN_ENTRY, KW_HEADERS   # noqa  # pylint: disable=unused-import
from hammock.resource import Resource  # noqa  # pylint: disable=unused-import
from hammock.api import Hammock  # noqa  # pylint:disable=unused-import


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
    warnings.warn('get_passthrough is deprecated, use get with dest= keyword argument instead', UserWarning)
    return wrappers.route(path, 'GET', dest=dest, **kwargs)


def post_passthrough(dest, path='', **kwargs):
    warnings.warn('post_passthrough is deprecated, use post with dest= keyword argument instead', UserWarning)
    return wrappers.route(path, 'POST', dest=dest, **kwargs)


def put_passthrough(dest, path='', **kwargs):
    warnings.warn('put_passthrough is deprecated, use put with dest= keyword argument instead', UserWarning)
    return wrappers.route(path, 'PUT', dest=dest, **kwargs)


def delete_passthrough(dest, path='', **kwargs):
    warnings.warn('delete_passthrough is deprecated, use delete with dest= keyword argument instead', UserWarning)
    return wrappers.route(path, 'DELETE', dest=dest, **kwargs)


def sink(path='', **kwargs):
    return wrappers.sink(path, **kwargs)

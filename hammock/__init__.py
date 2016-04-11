from __future__ import absolute_import
import hammock.wrappers as wrappers
from hammock.common import CONTENT_TYPE, CONTENT_LENGTH   # noqa  # pylint: disable=unused-import
from hammock.common import TYPE_JSON, TYPE_OCTET_STREAM, TOKEN_ENTRY, KW_HEADERS   # noqa  # pylint: disable=unused-import
from hammock.resource import Resource  # noqa  # pylint: disable=unused-import
from hammock.api import Hammock  # noqa  # pylint: disable=unused-import
import hammock.exceptions as exceptions  # noqa  # pylint: disable=unused-import
import hammock.types as types  # noqa  # pylint: disable=unused-import


FALCON = 'falcon'
AWEB = 'aweb'


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


def sink(path='', **kwargs):
    return wrappers.sink(path, **kwargs)

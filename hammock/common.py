from __future__ import absolute_import
try:
    import ujson as json
except ImportError:
    import json
import xml.etree.ElementTree as ElementTree
import codecs
import inspect
import logging
import random
import string

import six

import hammock.exceptions as exceptions

URL_PARAMS_METHODS = {'GET', 'HEAD', 'DELETE'}
KW_CONTENT = '_content'
KW_HEADERS = '_headers'
KW_CREDENTIALS = '_credentials'
KW_ENFORCER = '_enforcer'
KW_FILE = '_file'
KW_LIST = '_list'
KW_STATUS = '_status'
KW_HOST = '_host'
CONTENT_TYPE = 'CONTENT-TYPE'
CONTENT_LENGTH = 'CONTENT-LENGTH'
TYPE_JSON = 'application/json'
TYPE_XML = 'application/xml'
TYPE_TEXT_PLAIN = 'text/plain'
TYPE_OCTET_STREAM = 'application/octet-stream'
TOKEN_ENTRY = 'X-Auth-Token'
ID_LETTERS = (string.lowercase if six.PY2 else string.ascii_lowercase) + string.digits
ENCODING = 'utf-8'


# REST method names
PUT = 'PUT'
GET = 'GET'
POST = 'POST'
DELETE = 'DELETE'
PATCH = 'PATCH'

# REST methods not to log
REST_METHODS_LOGGING_BLACKLIST = [GET]

CONTENT_CONVERSION = {TYPE_JSON: json.dumps, TYPE_XML: ElementTree.tostring}


def url_join(*parts):
    return '/'.join(arg.strip('/') for arg in parts if arg)


def log_exception(exc, request_uuid):
    if isinstance(exc, exceptions.HttpError):
        logging.warning("[Http %s Exception %s] %s - %s", exc.status, request_uuid, exc.title, exc.description)
    else:
        logging.exception("[Internal server error %s]", request_uuid)


def is_valid_proxy_func(func):
    """
    Checks if a given function is valid for proxy endpoints.
    func should be either empty ('pass') or a generator
    """
    if inspect.isgeneratorfunction(func):
        return True

    lines = [line.strip() for line in inspect.getsource(func).split("\n")]
    while not lines.pop(0).startswith("def"):
        pass
    empty = "".join(lines).strip() == "pass"
    return empty


def uid(length=8):
    return ''.join(random.sample(ID_LETTERS, length))


def to_bytes(source):
    if isinstance(source, six.string_types):
        return codecs.encode(source, ENCODING)
    elif isinstance(source, six.moves.StringIO):
        # XXX: maybe more efficient way then reading StringIO data.
        return codecs.encode(source.getvalue(), ENCODING)
    return source

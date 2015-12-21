from __future__ import absolute_import
import six
import inspect
import hammock.exceptions as exceptions
import logging
import re
import functools
import codecs
import random
import string

URL_PARAMS_METHODS = {'GET', 'HEAD', 'DELETE'}
KW_CONTENT = '_content'
KW_HEADERS = '_headers'
KW_FILE = '_file'
KW_LIST = '_list'
KW_STATUS = '_status'
KW_TAIL = 'url_suffix_for_sink_methods'
CONTENT_TYPE = 'CONTENT-TYPE'
CONTENT_LENGTH = 'CONTENT-LENGTH'
TYPE_JSON = 'application/json'
TYPE_OCTET_STREAM = 'application/octet-stream'
TOKEN_ENTRY = 'X-Auth-Token'
PATH_TO_NAME = functools.partial(re.compile(r'[{}./-]').sub, '')
CONVERT_PATH_VARIABLES = functools.partial(re.compile(r'{([a-zA-Z][a-zA-Z_]*)}').sub, r'(?P<\1>[^/]+)')
ID_LETTERS = (string.lowercase if six.PY2 else string.ascii_lowercase) + string.digits
ENCODING = 'utf-8'


def url_join(*parts):
    return '/'.join(arg.strip('/') for arg in parts if arg)


def log_exception(exc, request_uuid):
    if isinstance(exc, exceptions.HttpError):
        logging.warning("[Http %s Exception %s] %s", exc.status, request_uuid, exc.title)
    else:
        logging.exception("[Internal server error %s]", request_uuid)


def func_is_pass(func):
    lines = [line.strip() for line in inspect.getsource(func).split("\n")]
    while not lines.pop(0).startswith("def"):
        pass
    empty = "".join(lines).strip() == "pass"
    if not empty:
        raise Exception("Passthrough function %s is not empty", func.__name__)


def uid(length=8):
    return ''.join(random.sample(ID_LETTERS, length))


def to_bytes(source):
    if isinstance(source, six.string_types):
        return codecs.encode(source, ENCODING)
    elif isinstance(source, six.moves.StringIO):
        # XXX: maybe more efficient way then reading StringIO data.
        return codecs.encode(source.getvalue(), ENCODING)
    return source

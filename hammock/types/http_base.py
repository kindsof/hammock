from __future__ import absolute_import
import io
try:
    import ujson as json
except ImportError:
    import json

import hammock.common as common
import hammock.exceptions as exceptions
from . import headers as _headers


def is_stream(obj):
    return hasattr(obj, 'read')


class HttpBase(object):
    """
    Base class for request and response object.
    Manage the headers and content of an HTTP request/response.
    """

    def __init__(self, headers, content):
        self._json = None
        self._content = None
        self.uid = common.uid()
        self.headers = _headers.Headers(headers)
        if isinstance(content, (list, dict)):
            self.json = content
        else:
            self._content = content

    @property
    def content(self):
        return self._content or ''

    @content.setter
    def content(self, content):
        self._content = content
        self.update_content_length()

    def read(self):
        if self.is_stream:
            self._content = self._content.read()
        return self.content

    @property
    def json(self):
        if self._json is None:
            body = self.read()
            if body:
                try:
                    self._json = json.loads(body)
                except (ValueError, UnicodeDecodeError) as exc:
                    raise exceptions.MalformedJson(
                        "Could not parse json body {!r}: {!r}".format(body, exc))
        return self._json

    @json.setter
    def json(self, data):
        self._json = data
        if data is None:
            self.content = None
        else:
            self.content = json.dumps(data)
            self.headers[common.CONTENT_TYPE] = common.TYPE_JSON

    @property
    def is_stream(self):
        return is_stream(self._content)

    def update_content_length(self):
        """
        Updates the content-length header, according to self._content
        """
        length = self._get_content_length()
        if length is not None:
            self.headers[common.CONTENT_LENGTH] = length

    def _get_content_length(self):
        if hasattr(self._content, '__len__'):
            return len(self._content)
        if hasattr(self._content, 'len'):
            return self._content.len
        elif isinstance(self._content, (io.StringIO, io.BytesIO)):
            try:
                self._content.seek(0, io.SEEK_END)
                return self._content.tell()
            finally:
                self._content.seek(0)
        return None

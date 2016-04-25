from __future__ import absolute_import
try:
    import ujson as json
except ImportError:
    import json
import six
import warnings
import httplib
import hammock.common as common
from . import headers as _headers


class Response(object):

    def __init__(self, content=None, headers=None, status=httplib.OK):
        self._json = None
        self.content = content
        self.headers = _headers.Headers(headers or {})
        self.status = str(status)

    @classmethod
    def from_result(cls, result=None, status=200, content_type=common.TYPE_JSON):
        """
        Create a response object from a response dict
        :param result: a result dict or list, a dict may contain special fields:
            - common.KW_HEADERS: set headers for the response
            - common.KW_FILE: set a content-stream to response
            - common.KW_LIST: set response body as a list
        :param status: status code for response
        :return: a Response object
        """
        result = cls._convert_result_to_dict(result)

        response_headers = _headers.Headers(result.pop(common.KW_HEADERS, {}))
        content_stream = result.pop(common.KW_FILE, None)
        response_status = result.pop(common.KW_STATUS, status)

        if content_stream:
            content = common.to_bytes(content_stream)
            response_headers[common.CONTENT_TYPE] = common.TYPE_OCTET_STREAM
            length = common.get_stream_length(content)
            if length:
                response_headers[common.CONTENT_LENGTH] = length
            response_headers.update(result)
        elif content_type == common.TYPE_JSON:
            if common.KW_CONTENT in result:
                content = result.pop(common.KW_CONTENT)
                response_headers.update(result)
            else:
                content = result
            if content is not None:
                content = json.dumps(content)
                response_headers.update({
                    common.CONTENT_LENGTH: len(content),
                    common.CONTENT_TYPE: common.TYPE_JSON,
                })
        else:
            response_headers[common.CONTENT_TYPE] = content_type
            content = result[common.KW_CONTENT]

        return cls(content, response_headers, response_status)

    def set_header(self, key, value):
        warnings.warn('set_header is deprecated, use headers[key] = value instead', UserWarning)
        self.headers[key] = value

    @property
    def body(self):
        warnings.warn('body is deprecated, use .content instead', UserWarning)
        return self.content

    @property
    def stream(self):
        warnings.warn('stream is deprecated, use .content instead', UserWarning)
        return self.content

    @property
    def is_stream(self):
        return hasattr(self.content, 'read')

    @property
    def json(self):
        if not self._json:
            self._json = json.load(self.content) if self.is_stream else json.loads(self.content)
        return self._json

    @json.setter
    def json(self, data):
        self.content = json.dumps(data)
        self.headers.update({
            common.CONTENT_LENGTH: len(self.content),
            common.CONTENT_TYPE: common.TYPE_JSON,
        })

    @classmethod
    def _convert_result_to_dict(cls, result):
        if isinstance(result, dict):
            return result
        elif isinstance(result, (list, six.string_types, six.binary_type, bool, type(None))):
            return {common.KW_CONTENT: result}
        else:
            return {common.KW_FILE: result}

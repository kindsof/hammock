from __future__ import absolute_import
import six
import warnings
import hammock.common as common
import hammock.headers as headers_module
import simplejson as json


class Response(object):

    def __init__(self, content, headers, status):
        self.content = content
        self.headers = headers_module.Headers(headers)
        self.status = str(status)

    @classmethod
    def from_result(cls, result=None, status=200):
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

        response_headers = headers_module.Headers(result.pop(common.KW_HEADERS, {}))
        content_stream = result.pop(common.KW_FILE, None)
        response_status = result.pop(common.KW_STATUS, status)
        content = result.pop(common.KW_CONTENT, None)

        if content_stream:
            content = content_stream
            response_headers.update({
                common.CONTENT_TYPE: common.TYPE_OCTET_STREAM,
            })
            response_headers.update(result)
        else:
            if content is not None:
                content = json.dumps(content)
                response_headers.update(result)
            else:
                content = json.dumps(result)
            response_headers.update({
                common.CONTENT_LENGTH: len(content),
                common.CONTENT_TYPE: common.TYPE_JSON,
            })
        return cls(content, response_headers, response_status)

    def update_falcon(self, response):
        response.status = self.status
        for key, value in six.iteritems(self.headers):
            response.set_header(key, value)
        if hasattr(self.content, 'read'):
            response.stream = self.content
        else:
            response.body = self.content

    def set_header(self, key, value):
        warnings.warn('set_header is deprecated, use headers[key] = value instead', DeprecationWarning)
        self.headers[key] = value

    @property
    def body(self):
        warnings.warn('body is deprecated, use .content instead', DeprecationWarning)
        return self.content

    @property
    def stream(self):
        warnings.warn('stream is deprecated, use .content instead', DeprecationWarning)
        return self.content

    @classmethod
    def _convert_result_to_dict(cls, result):
        if result is None:
            return {}
        elif isinstance(result, dict):
            return result
        elif isinstance(result, (list, six.string_types, six.binary_type, bool)):
            return {common.KW_CONTENT: result}
        else:
            return {common.KW_FILE: result}

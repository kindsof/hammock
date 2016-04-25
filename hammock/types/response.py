from __future__ import absolute_import
try:
    import ujson as json
except ImportError:
    import json
import httplib
import hammock.common as common
from . import http_base as http_base


class Response(http_base.HttpBase):

    def __init__(self, content=None, headers=None, status=httplib.OK):
        """
        Create a response object
        :param content: Content of response, might be a file-like object
            or any jsonable object.
        :param headers: headers of response.
        :param status: status code of response.
        """
        super(Response, self).__init__(headers, content)
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

        response_headers = result.pop(common.KW_HEADERS, {})
        content_stream = result.pop(common.KW_FILE, None)
        response_status = result.pop(common.KW_STATUS, status)

        if content_stream:
            content = common.to_bytes(content_stream)
            response_headers[common.CONTENT_TYPE] = common.TYPE_OCTET_STREAM
            response_headers.update(result)
        elif content_type == common.TYPE_JSON:
            if common.KW_CONTENT in result:
                content = result.pop(common.KW_CONTENT)
                response_headers.update(result)
                if content is not None:
                    content = json.dumps(content)
            else:
                content = result
        else:
            response_headers[common.CONTENT_TYPE] = content_type
            content = result[common.KW_CONTENT]

        return cls(content, response_headers, response_status)

    @classmethod
    def _convert_result_to_dict(cls, result):
        """
        Convert any result into a dict-result.
        :param result:
        :return:
        """
        if isinstance(result, dict):
            return result
        elif not http_base.is_stream(result):
            return {common.KW_CONTENT: result}
        else:
            return {common.KW_FILE: result}

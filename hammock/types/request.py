from __future__ import absolute_import

import copy
import logging

import hammock.common as common
from . import url as _module
from . import file as file_module
from . import http_base as http_base

LOG = logging.getLogger(__name__)


class Request(http_base.HttpBase):

    def __init__(self, method, url, headers, content, url_params):
        super(Request, self).__init__(headers, content)
        self.method = method.upper()
        self._collected_data = None
        self._url = _module.Url(url)
        self.url_params = url_params
        LOG.debug('[request %s] %s %s', self.uid, self.method, self.url)

    @property
    def url(self):
        return self._url.url

    @property
    def parsed_url(self):
        return self._url.parsed

    @property
    def path(self):
        return self._url.path

    @path.setter
    def path(self, path):
        self._url.path = path

    @property
    def scheme(self):
        return self._url.scheme

    @property
    def query(self):
        return self._url.query

    @property
    def params(self):
        return self._url.params

    @property
    def relative_uri(self):
        return self._url.path + (('?' + self._url.query) if self._url.query else '')

    @property
    def collected_data(self):
        """
        Generate data object combined out of query params, json body, or streamed data.
        :return: A dict, query params override by json body if relevant.
            Special fields:
            - common.KW_FILE: a hammock.types.file.File object containing a stream if content-type is octet-stream.
            - common.KW_LIST: a list, if content-type is json and the content is of type list.
        """
        if not self._collected_data:
            self._collected_data = copy.deepcopy(self.params)
            if self.method not in common.URL_PARAMS_METHODS:
                body = self._collect_body()
                if body:
                    self._collected_data.update(body)
            self._collected_data.update(self.url_params)
        return self._collected_data.copy()

    def trim_prefix(self, prefix):
        """
        Trims a prefix from the request's path
        :param prefix: A prefix to trim
        """
        self.path = self.path.lstrip("/")[len(prefix.strip("/")):]

    def _collect_body(self):
        content_type = self.headers.get(common.CONTENT_TYPE, '')
        if common.TYPE_JSON in content_type:
            body = self.json
            if isinstance(body, dict):
                return body
            elif isinstance(body, list):
                return {common.KW_LIST: body}
            elif body is None:
                return None
            else:
                return {common.KW_CONTENT: body}
        elif common.TYPE_OCTET_STREAM in content_type:
            return {common.KW_FILE: file_module.File(self.content, self.headers.get(common.CONTENT_LENGTH))}

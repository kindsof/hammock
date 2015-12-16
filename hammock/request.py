from __future__ import absolute_import

import copy

import simplejson as json
import six
import six.moves.urllib as urllib  # pylint: disable=import-error
import logging
from hammock import common
from hammock import exceptions

from hammock import types

LOG = logging.getLogger(__name__)


class Request(object):
    def __init__(self, method, url, headers, stream):
        self.method = method.upper()
        self._url = None
        self._parsed_url = None
        self._params = None
        self._collected_data = None
        self.url = url
        self.headers = types.Headers(headers)
        self.stream = stream
        self.uid = common.uid()
        LOG.debug('[request %s] %s %s', self.uid, self.method, self.url)

    @classmethod
    def from_falcon(cls, req):
        return Request(req.method, req.url, req.headers, req.stream)

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url
        self._parsed_url = None
        self._params = None

    @property
    def parsed_url(self):
        """lazy evaluation of parsed url"""
        if not self._parsed_url:
            self._parsed_url = urllib.parse.urlparse(self.url)
        return self._parsed_url

    @property
    def path(self):
        return self.parsed_url.path

    @path.setter
    def path(self, path):
        path = '/' + path.lstrip('/')
        new_url = urllib.parse.urljoin(self.url, path)
        if self.parsed_url.query:
            new_url += '?' + self.parsed_url.query
        self.url = new_url

    @property
    def scheme(self):
        return self.parsed_url.scheme

    @property
    def query(self):
        return self.parsed_url.query

    @property
    def params(self):
        if not self._params:
            self._params = {
                key: self._param_value(value)
                for key, value in six.iteritems(urllib.parse.parse_qs(self.parsed_url.query))
                }
        return self._params

    @property
    def _cached_headers(self):  # XXX: backward compatibility, should be removed
        return self.headers

    @property
    def collected_data(self):
        """
        Generate data object combined out of query params, json body, or streamed data.
        :return: A dict, query params override by json body if relevant.
            Special fields:
            - common.KW_FILE: a types.File object containing a stream if content-type is octet-stream.
            - common.KW_LIST: a list, if content-type is json and the content is of type list.
        """
        if not self._collected_data:
            self._collected_data = copy.deepcopy(self.params)
            if self.method not in common.URL_PARAMS_METHODS:
                self._collected_data.update(self._collect_body())
        return self._collected_data.copy()

    def _collect_body(self):
        content_type = self.headers.get(common.CONTENT_TYPE)
        if content_type == common.TYPE_JSON:
            try:
                body = json.load(self.stream)
                if type(body) == dict:
                    return body
                elif type(body) == list:
                    return {common.KW_LIST: body}
            except (ValueError, UnicodeDecodeError):
                raise exceptions.MalformedJson()
        elif content_type == common.TYPE_OCTET_STREAM:
            return {common.KW_FILE: types.File(self.stream, self.headers.get(common.CONTENT_LENGTH))}

    @staticmethod
    def _param_value(value):
        if len(value) > 1:
            return value
        value = value[0]
        return value if value != 'None' else None

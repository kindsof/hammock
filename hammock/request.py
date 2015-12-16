from __future__ import absolute_import
import copy
import six
import requests
import simplejson as json
import logging

import warnings

from hammock import common
from hammock import exceptions
from hammock import types
from hammock import url as url_module

LOG = logging.getLogger(__name__)


class Request(object):
    def __init__(self, method, url, headers, stream):
        self.method = method.upper()
        self._collected_data = None
        self._url = url_module.Url(url)
        self.headers = types.Headers(headers)
        self.stream = stream
        self.uid = common.uid()
        LOG.debug('[request %s] %s %s', self.uid, self.method, self.url)

    @classmethod
    def from_falcon(cls, req):
        return Request(req.method, req.url, req.headers, req.stream)

    @property
    def url(self):
        return self._url.url

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
    def _cached_headers(self):  # XXX: backward compatibility, should be removed
        warnings.warn('_cached_headers is deprecated, use headers', DeprecationWarning)
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

    def trim_prefix(self, prefix):
        """
        Trims a prefix from the request's path
        :param prefix: A prefix to trim
        """
        self.path = self.path.lstrip("/")[len(prefix.strip("/")):]

    def set_content(self, content):
        self.stream = content
        self.headers[common.CONTENT_LENGTH] = len(content)

    def send_to(self, dest):
        redirection_url = common.url_join(dest, self.path) + '?' + self.query
        logging.info('[Passthrough %s] redirecting to %s', self.uid, redirection_url)
        inner_request = requests.Request(
            self.method,
            url=redirection_url,
            data=self.stream if self.method not in common.URL_PARAMS_METHODS else None,
            headers={
                k: v if k.lower() != "host" else six.moves.urllib.parse.urlparse(dest).netloc
                for k, v in six.iteritems(self.headers)
                if v != ""
            },
        )
        session = requests.Session()
        try:
            prepared = session.prepare_request(inner_request)
            if self.headers.get(common.CONTENT_LENGTH):
                prepared.headers[common.CONTENT_LENGTH] = self.headers.get(common.CONTENT_LENGTH)
            if self.headers.get('TRANSFER-ENCODING'):
                del prepared.headers['TRANSFER-ENCODING']
            inner_response = session.send(prepared, stream=True)
            return types.Response(inner_response.raw, inner_response.headers, inner_response.status_code)
        finally:
            session.close()

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

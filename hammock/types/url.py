from __future__ import absolute_import
import six
import six.moves.urllib as urllib  # pylint: disable=import-error


class Url(object):

    def __init__(self, url):
        self._url = None
        self._parsed = None
        self._params = None
        self.url = url

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url
        self._parsed = None
        self._params = None

    @property
    def parsed(self):
        """lazy evaluation of parsed url"""
        if not self._parsed:
            self._parsed = urllib.parse.urlparse(self.url)
        return self._parsed

    @property
    def path(self):
        return self.parsed.path

    @path.setter
    def path(self, path):
        path = '/' + path.lstrip('/')
        new_url = urllib.parse.urljoin(self.url, path)
        if self.parsed.query:
            new_url += '?' + self.parsed.query
        self.url = new_url

    @property
    def scheme(self):
        return self.parsed.scheme

    @property
    def query(self):
        return self.parsed.query

    @property
    def params(self):
        if not self._params:
            self._params = {
                key: self._param_value(value)
                for key, value in six.iteritems(urllib.parse.parse_qs(self.parsed.query))
                }
        return self._params

    @staticmethod
    def _param_value(value):
        if len(value) > 1:
            return value
        value = value[0]
        return value if value != 'None' else None

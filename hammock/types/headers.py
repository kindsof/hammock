from __future__ import absolute_import
import requests.structures as structures


class Headers(structures.CaseInsensitiveDict):

    def __setitem__(self, key, value):
        super(Headers, self).__setitem__(key, str(value) if not isinstance(value, six.string_types) else value)

    def __call__(self, key):
        return self.get(key)

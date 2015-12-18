from __future__ import absolute_import
import falcon.util.structures as structures


class Headers(structures.CaseInsensitiveDict):
    def __init__(self, headers):
        super(Headers, self).__init__(headers)

    def __setitem__(self, key, value):
        super(Headers, self).__setitem__(key, str(value))

    def __call__(self, key):
        return self.get(key)

import falcon.util.structures as structures
import collections


Response = collections.namedtuple("Response", ["stream", "headers", "status"])
File = collections.namedtuple("File", ["stream", "content_length"])


class Headers(structures.CaseInsensitiveDict):

    def __init__(self, headers):
        super(Headers, self).__init__(headers)

    def __call__(self, key):
        return self.get(key)

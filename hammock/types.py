import collections


Response = collections.namedtuple("Response", ["stream", "headers", "status"])

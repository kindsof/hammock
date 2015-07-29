import falcon.util.structures as structures


class Headers(structures.CaseInsensitiveDict):

    def __init__(self, headers):
        super(Headers, self).__init__(headers)

    def __call__(self, key):
        return self.get(key)

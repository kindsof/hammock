

def url_join(*parts):
    return '/'.join(arg.strip('/') for arg in parts if arg)


class HeaderWrapper(object):

    def __init__(self, headers):
        self._headers = headers
        self._extras = {}

    def __call__(self, key):
        return self._extras[key] if key in self._extras else self._headers(key)

    def __setitem__(self, key, value):
        self._extras[key] = value

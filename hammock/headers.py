class Headers(dict):

    def __init__(self, headers, handler):
        super(Headers, self).__init__(headers)
        self._handler = handler

    def __call__(self, key):
        return self._handler(key)

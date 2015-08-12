import falcon
from hammock import resource


class Dict(resource.Resource):

    def __init__(self, *args):
        super(Dict, self).__init__(*args)
        self._dict = {}

    @resource.post("{key}")
    def item_create(self, key, value):  # pylint: disable=unused-argument
        if key in self._dict:
            raise falcon.HTTPError(falcon.HTTP_400, "400")
        self._dict[key] = value
        return {"post": value}

    @resource.get("{key}")
    def item_get(self, key):  # pylint: disable=unused-argument
        if key not in self._dict:
            raise falcon.HTTPError(falcon.HTTP_404, "404")
        return {"get": self._dict[key]}

    @resource.put("{key}")
    def item_change(self, key, value):  # pylint: disable=unused-argument
        if key not in self._dict:
            raise falcon.HTTPError(falcon.HTTP_404, "404")
        self._dict[key] = value
        return {"put": value}

    @resource.delete("{key}")
    def item_delete(self, key):  # pylint: disable=unused-argument
        if key not in self._dict:
            raise falcon.HTTPError(falcon.HTTP_404, "404")
        value = self._dict[key]
        del self._dict[key]
        return {"delete": value}

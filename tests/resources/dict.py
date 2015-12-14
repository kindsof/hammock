from __future__ import absolute_import
import hammock.resource as resource
import hammock.exceptions as exceptions


class KeyNotFound(exceptions.NotFound):
    def __init__(self):  # pylint: disable=super-on-old-class
        super(KeyNotFound, self).__init__('Key not found')


class Dict(resource.Resource):

    def __init__(self, *args):
        super(Dict, self).__init__(*args)
        self._dict = {}

    @resource.post("{key}")
    def item_create(self, key, value):  # pylint: disable=unused-argument
        if key in self._dict:
            raise exceptions.BadRequest('Key already exists')
        self._dict[key] = value
        return {"post": value}

    @resource.get("{key}")
    def item_get(self, key):  # pylint: disable=unused-argument
        if key not in self._dict:
            raise KeyNotFound()
        return {"get": self._dict[key]}

    @resource.put("{key}")
    def item_change(self, key, value):  # pylint: disable=unused-argument
        if key not in self._dict:
            raise KeyNotFound()
        self._dict[key] = value
        return {"put": value}

    @resource.delete("{key}")
    def item_delete(self, key):  # pylint: disable=unused-argument
        if key not in self._dict:
            raise KeyNotFound()
        value = self._dict[key]
        del self._dict[key]
        return {"delete": value}

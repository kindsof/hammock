from __future__ import absolute_import
import hammock.resource_node as resource_node
import hammock.backends as backends


try:
    import falcon
except ImportError:
    falcon = None
try:
    import aiohttp.web as aweb
except ImportError:
    aweb = None


class Hammock(resource_node.ResourceNode):

    def __init__(self, api, resource_package):
        self._api = api
        self._backend = None
        if falcon and isinstance(api, falcon.API):
            self._backend = backends.Falcon(api)
        elif aweb and isinstance(api, aweb.Application):
            self._backend = backends.AWeb(api)
        self._backend.add_resources(self, resource_package)

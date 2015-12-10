from __future__ import absolute_import
from hammock import resource


class Keywords(resource.Resource):

    DEFAULT = 10

    @resource.get()
    def get(self, arg, default=DEFAULT, **kwargs):
        return self._answer(arg, default, **kwargs)

    @resource.post()
    def post(self, arg, default=DEFAULT, **kwargs):
        return self._answer(arg, default, **kwargs)

    @resource.put()
    def put(self, arg, default=DEFAULT, **kwargs):
        return self._answer(arg, default, **kwargs)

    @resource.get("headers")
    def get_with_headers(self, arg, _headers, default=10, **kwargs):
        return self._answer(arg, default, headers=dict(_headers), **kwargs)

    def _answer(self, arg, default, **kwargs):
        ret = {
            "arg": arg,
            "default": default,
        }
        ret.update(kwargs)
        return ret

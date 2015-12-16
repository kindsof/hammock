from __future__ import absolute_import
from hammock import resource


class Hello(resource.Resource):
    @resource.get()
    def hello(self, name):
        return {'hello': name}

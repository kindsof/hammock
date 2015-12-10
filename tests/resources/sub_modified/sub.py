from __future__ import absolute_import
from hammock import resource


class Sub(resource.Resource):
    PATH = "different_sub"

    @resource.get()
    def test_headers(self):
        return "modified-in-modified"

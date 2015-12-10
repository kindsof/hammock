from __future__ import absolute_import
from hammock import resource


class Sub(resource.Resource):

    @resource.get()
    def test_headers(self):
        return "sub-in-nested-in-sub"

from __future__ import absolute_import
import hammock


class Sub(hammock.Resource):

    @hammock.get()
    def test_headers(self):
        return "sub-in-sub2"

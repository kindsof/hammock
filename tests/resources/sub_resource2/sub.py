from __future__ import absolute_import
import hammock


class Sub(hammock.Resource):

    POLICY_GROUP_NAME = False

    @hammock.get()
    def test_headers(self):
        return "sub-in-sub2"

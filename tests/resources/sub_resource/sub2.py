from __future__ import absolute_import
import hammock


class Sub2(hammock.Resource):

    POLICY_GROUP_NAME = False

    @hammock.get()
    def test_headers(self):
        return "sub2-in-sub1"

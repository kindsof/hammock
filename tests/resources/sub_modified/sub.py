from __future__ import absolute_import
import hammock


class Sub(hammock.Resource):
    PATH = "different_sub"
    POLICY_GROUP_NAME = False

    @hammock.get()
    def test_headers(self):
        return "modified-in-modified"

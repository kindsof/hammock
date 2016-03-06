from __future__ import absolute_import
import hammock


class Sub(hammock.Resource):

    POLICY_GROUP_NAME = False

    @hammock.get()
    def get(self):
        return "sub-in-sub2"

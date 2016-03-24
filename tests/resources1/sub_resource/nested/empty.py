from __future__ import absolute_import
import hammock


class Empty(hammock.Resource):

    POLICY_GROUP_NAME = False
    PATH = ''

    @hammock.get('additional')
    def additional(self):
        return 'additional'

    @hammock.get('additional-2')
    def additional_2(self):
        return 'additional-2'

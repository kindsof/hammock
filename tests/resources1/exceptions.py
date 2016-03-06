from __future__ import absolute_import
import hammock
import hammock.exceptions as exceptions

DESCRIPTION = 'This exception is intentional'


class Exceptions(hammock.Resource):

    POLICY_GROUP_NAME = False

    @hammock.get('internal')
    def internal(self):
        raise Exception(DESCRIPTION)

    @hammock.get('not_found')
    def not_found(self):
        raise exceptions.NotFound(DESCRIPTION)

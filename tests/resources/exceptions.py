from __future__ import absolute_import
import hammock.resource as resource
import hammock.exceptions as exceptions

DESCRIPTION = 'This exception is intentional'


class Exceptions(resource.Resource):

    @resource.get('internal')
    def internal(self):
        raise Exception(DESCRIPTION)

    @resource.get('not_found')
    def not_found(self):
        raise exceptions.NotFound(DESCRIPTION)

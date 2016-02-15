from __future__ import absolute_import
import hammock
import six


class Responses(hammock.Resource):

    POLICY_GROUP_NAME = False

    @hammock.get(path='none')
    def none(self):
        return None

    @hammock.get(path='string')
    def string(self):
        return 'string'

    @hammock.get(path='string-io')
    def string_io(self):
        return six.moves.StringIO('string')

    @hammock.get(path='bytes')
    def bytes(self):
        return b'bytes'

    @hammock.get(path='bytes-io')
    def bytes_io(self):
        return six.BytesIO(b'bytes')

    @hammock.get(path='list')
    def list(self):
        return [1, 2, 3]

from __future__ import absolute_import
import hammock
import hammock.exceptions as exceptions

DESCRIPTION = 'This exception is intentional'


class Exceptions(hammock.Resource):

    @hammock.get('internal')
    def internal(self):
        raise Exception(DESCRIPTION)

    @hammock.get('not_found')
    def not_found(self):
        raise exceptions.NotFound(DESCRIPTION)

    @hammock.post('raise-with-stream')
    def raise_with_stream(self, _file):  # pylint: disable=unused-argument
        # Do not read file, but raise exception.
        # If server do not read all the file before returning a response,
        # a Connection-Aborted will be shown in the client.
        raise exceptions.BadRequest(DESCRIPTION)

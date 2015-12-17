from __future__ import absolute_import
import hammock


class Responses(hammock.Resource):

    @hammock.get(path='none')
    def none(self):
        return None

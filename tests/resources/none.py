from __future__ import absolute_import
import hammock


class NoneTest(hammock.Resource):
    PATH = 'none'

    @hammock.get()
    def none(self):
        return None

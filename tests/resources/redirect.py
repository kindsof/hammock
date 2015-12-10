from __future__ import absolute_import
from hammock import resource


PORT = 12345
DEST = "http://localhost:{:d}".format(PORT)


class Redirect(resource.Resource):

    @resource.passthrough(dest=DEST, trim_prefix="redirect")
    def passthrough(self):
        pass

    @resource.get("specific")
    def specific(self):
        return "specific"

from hammock import resource


PORT = 12345
DEST = "http://localhost:{:d}".format(PORT)


class Redirect(resource.Resource):

    @resource.passthrough(dest=DEST)
    def passthrough(self):
        pass

    @resource.get("specific")
    def specific(self):
        return "specific"

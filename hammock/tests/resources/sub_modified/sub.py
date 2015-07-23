from hammock import resource


class Sub(resource.Resource):

    @resource.get()
    def test_headers(self):
        return "sub-in-modified"

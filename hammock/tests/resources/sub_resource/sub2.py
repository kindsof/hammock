from hammock import resource


class Sub2(resource.Resource):

    @resource.get()
    def test_headers(self):
        return "sub2-in-sub1"

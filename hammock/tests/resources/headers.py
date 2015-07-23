from hammock import resource


class Headers(resource.Resource):

    @resource.get("{key}")
    def request_headers(self, key, value, _headers):
        return _headers(key) == value

    @resource.get()
    def response_headers(self):
        return {resource.KW_HEADERS: {"some_key": "some_value"}}

from __future__ import absolute_import
from hammock import resource


class Headers(resource.Resource):

    @resource.get("{key}")
    def request_headers(self, key, value, _headers):
        return _headers(key) == value

    @resource.get()
    def response_headers(self, _headers):
        return {resource.KW_HEADERS: _headers}

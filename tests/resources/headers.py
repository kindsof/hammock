from __future__ import absolute_import
import hammock
import hammock.common as common


class Headers(hammock.Resource):

    POLICY_GROUP_NAME = False

    @hammock.get("{key}")
    def request_headers(self, key, value, _headers):
        return _headers(key) == value

    @hammock.get()
    def response_headers(self, _headers):
        return {common.KW_HEADERS: _headers}

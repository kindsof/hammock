import json
import falcon
import hammock
import falcon.testing as testing
import tests.resources as resources
import hammock.common as common


class TestResource(testing.TestBase):
    def setUp(self):
        super(TestResource, self).setUp()
        self.api = falcon.API()
        hammock.Hammock(self.api, resources)

    def test_patterns(self):
        url = "/patterns"

        response = self._simulate("GET", url)
        self.assertEquals(response, "base")

        response = self._simulate("GET", url + "/123")
        self.assertEquals(response, "id-123")

        response = self._simulate("GET", url + "/123/extra")
        self.assertEquals(response, "extra-123")

    def _simulate(self, method, url, query_string=None, body=None, headers=None):
        kwargs = {}
        headers = headers or {}
        if query_string:
            kwargs["query_string"] = query_string
        if body:
            kwargs["body"] = json.dumps(body)
            headers.update({common.CONTENT_TYPE: common.TYPE_JSON})
        kwargs["headers"] = headers
        for resp in self.simulate_request(url, method=method, **kwargs):  # pylint: disable=star-args
            return json.loads(resp)

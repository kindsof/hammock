import os
import json
import falcon
import logging
import falcon.testing as testing
import hammock
import hammock.common as common
import hammock.types as hammock_types
import tests.resources as resources
import tests.resources.keywords as keywords


def default_404(req, res):  # pylint: disable=unused-argument
    raise falcon.HTTPError(falcon.HTTP_404, "404")


class TestResource(testing.TestBase):

    def setUp(self):
        super(TestResource, self).setUp()
        self.api = falcon.API()
        hammock.Hammock(self.api, resources)
        self.api.add_sink(default_404)

    def test_resource(self):
        dict_url = lambda key: "/dict/%s" % key
        self.assertDictEqual({"post": 1}, self._simulate("POST", dict_url("a"), body={"value": 1}))
        self.assertDictEqual({"post": 2}, self._simulate("POST", dict_url("b"), body={"value": 2}))
        self.assert_400("POST", dict_url("a"), body={"value": 10})
        self.assertDictEqual({"get": 1}, self._simulate("GET", dict_url("a")))
        self.assertDictEqual({"get": 2}, self._simulate("GET", dict_url("b")))
        self.assertDictEqual({"put": 10}, self._simulate("PUT", dict_url("a"), body={"value": 10}))
        self.assertDictEqual({"get": 10}, self._simulate("GET", dict_url("a")))
        self.assertDictEqual({"delete": 10}, self._simulate("DELETE", dict_url("a")))
        self.assert_404("DELETE", dict_url("a"))
        self.assert_404("GET", dict_url("a"))
        self.assert_404("PUT", dict_url("a"), body={"value": "1"})
        self.assertEqual("HELLO", self._simulate("GET", "/text/upper/hello"))
        self.assertEqual("helly", self._simulate("GET", "/text/replace/hello", query_string="old=o&new=y"))
        self.assertEqual("hallo", self._simulate("PUT", "/text/replace/hello", body={"old": "e", "new": "a"}))
        self.assertEqual("hallo", self._simulate("POST", "/text/replace/hello", body={"old": "e", "new": "a"}))
        self.assertEqual("helly", self._simulate("DELETE", "/text/replace/hello", query_string="old=o&new=y"))

    def test_files(self):
        path = "/files"
        mb_to_test = 100
        logging.info("Testing post and get of %d mb", mb_to_test)
        body = bytearray(mb_to_test << 20)
        response = self.simulate_request(
            path,
            method="POST",
            body=body,
            headers={common.CONTENT_TYPE: common.TYPE_OCTET_STREAM},
        )
        response = list(response)
        self.assertLess(1, len(response))
        result = "".join(response)
        self.assertEquals(result, body)

        logging.info("Testing get of %d mb", mb_to_test)
        response = self.simulate_request(
            path,
            method="GET",
            query_string="size_mb={:d}".format(mb_to_test)
        )
        response = list(response)
        self.assertLess(1, len(response))
        result = "".join(response)
        self.assertLess(mb_to_test, result.__sizeof__() >> 10)
        logging.info("Testing reading in server of %d mb", mb_to_test)
        response = self.simulate_request(
            os.path.join(path, "check_size"),
            method="POST",
            query_string="size_mb={:d}".format(mb_to_test),
            body=body,
            headers={common.CONTENT_TYPE: common.TYPE_OCTET_STREAM},
        )
        self.assertEqual(json.loads(response[0]), "OK")

    def test_sink(self):
        self.assert_404("GET", "/get_something_wrong")
        self.assert_404("GET", "/get_something_wrong/with_query", query_string="a=b")
        self.assert_404("PUT", "/put_something_wrong")
        self.assert_404("PUT", "/put_something_wrong/with_body", body={"value": "1"})
        self.assert_404("POST", "/post_something_wrong")
        self.assert_404("POST", "/post_something_wrong/with_body", body={"value": "1"})
        self.assert_404("delete", "/delete_something_wrong")
        self.assert_404("DELETE", "/delete_something_wrong/with_query", query_string="a=b")

    def test_sub_resource(self):
        self.assertEqual("sub-in-sub1", self._simulate("GET", "/sub_resource/sub"))
        self.assertEqual("sub2-in-sub1", self._simulate("GET", "/sub_resource/sub2"))
        self.assertEqual("sub-in-sub2", self._simulate("GET", "/sub_resource2/sub"))
        self.assertEqual("modified-in-modified", self._simulate("GET", "/different_path/different_sub"))
        self.assertEqual("sub-in-nested-in-sub", self._simulate("GET", "/sub_resource/nested/sub"))

    def test_internal_server_error(self):
        logging.info("Testing for exception raising")
        self.assertRaises(Exception, self._simulate, "GET", "/text/raise_exception")

    def test_headers(self):
        headers = {"key1": "value1", "key2": "value2"}
        for k, v in headers.iteritems():
            self.assertEquals(
                True,
                self._simulate("GET", "/headers/%s" % k, query_string="value=%s" % v, headers=headers)
            )
        self.assertEquals(
            False,
            self._simulate("GET", "/headers/%s" % headers.keys()[0], query_string="value=some_wrong_value", headers=headers)
        )
        self.assertEquals(
            True,
            self._simulate("GET", "/headers/some_wrong_key", query_string="value=None", headers=headers)
        )

    def test_keywords(self):
        url = "/keywords"
        expected = {"arg": 1, "default": 2, "c": 3, "d": 4}
        expected_no_default = expected.copy()
        expected_no_default["default"] = keywords.Keywords.DEFAULT

        logging.info("Testing keywords with GET")
        get = self._simulate(
            "GET", url,
            query_string="arg=1&default=2&c=3&d=4",
        )
        self.assertDictEqual({k: int(v) for k, v in get.iteritems()}, expected)

        logging.info("Testing keywords with GET and no default")
        get = self._simulate(
            "GET", url,
            query_string="arg=1&c=3&d=4",
        )
        self.assertDictEqual({k: int(v) for k, v in get.iteritems()}, expected_no_default)

        for method in ("POST", "PUT"):
            logging.info("Testing keywords with %s", method)
            ret = self._simulate(
                method, url,
                body=expected,
            )
            self.assertDictEqual(ret, expected)
            no_default = expected.copy()
            del no_default["default"]
            ret = self._simulate(
                method, url,
                body=no_default,
            )
            self.assertDictEqual(ret, expected_no_default)
        logging.info("Testing keywords with GET and headers")
        response = self._simulate(
            "GET", "{}/headers".format(url),
            query_string="arg=1&default=2&c=3",
            headers={"d": str(expected["d"])},
        )
        self.assertEqual(int(response["arg"]), expected["arg"])
        self.assertEqual(int(response["default"]), expected["default"])
        self.assertEqual(int(response["c"]), expected["c"])
        headers = hammock_types.Headers(response["headers"])
        self.assertEqual(int(headers["d"]), expected["d"])

    def _simulate(self, method, url, query_string=None, body=None, headers=None):
        kwargs = {}
        headers = headers or {}
        if query_string:
            kwargs["query_string"] = query_string
        if body:
            kwargs["body"] = json.dumps(body)
            headers.update({common.CONTENT_TYPE: common.TYPE_JSON})
        kwargs["headers"] = headers
        return json.loads(self.simulate_request(url, method=method, **kwargs)[0])  # pylint: disable=star-args

    def assert_404(self, *args, **kwargs):
        self.assertDictEqual({"title": "404"}, self._simulate(*args, **kwargs))

    def assert_400(self, *args, **kwargs):
        self.assertDictEqual({"title": "400"}, self._simulate(*args, **kwargs))

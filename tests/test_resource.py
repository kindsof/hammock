from __future__ import absolute_import
import tests.base as base
import six
import os
import logging
import hammock.common as common
import hammock.types as hammock_types
import tests.resources.keywords as keywords


class TestResource(base.TestBase):

    def test_resource(self):
        def dict_url(key):
            return "/dict/%s" % key

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
        response = self._simulate(
            "POST",
            path,
            body=body,
            headers={
                common.CONTENT_TYPE: common.TYPE_OCTET_STREAM,
                common.CONTENT_LENGTH: str(len(body)),
            },
        )
        if not isinstance(response, six.binary_type):
            body = body.decode()
        self.assertEqual(response, body)

        logging.info("Testing get of %d mb", mb_to_test)
        response = self._simulate(
            "GET",
            path,
            query_string="size_mb={:d}".format(mb_to_test)
        )
        size_bytes = len(response) if not isinstance(response, six.binary_type) else response.__sizeof__()
        self.assertEqual(mb_to_test, size_bytes >> 20)
        logging.info("Testing reading in server of %d mb", mb_to_test)
        response = self._simulate(
            "POST",
            os.path.join(path, "check_size"),
            query_string="size_mb={:d}".format(mb_to_test),
            body=body,
            headers={common.CONTENT_TYPE: common.TYPE_OCTET_STREAM},
        )
        self.assertEqual(response, "OK")

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
        self._simulate('GET', '/text/raise_exception')
        self.assertIn('500', self.srmock.status)

    def test_headers(self):
        headers = {"key1": "value1", "key2": "value2"}
        for k, v in six.iteritems(headers):
            self.assertEqual(
                True,
                self._simulate("GET", "/headers/%s" % k, query_string="value=%s" % v, headers=headers)
            )
        self.assertEqual(
            False,
            self._simulate("GET", "/headers/%s" % next(six.iterkeys(headers)), query_string="value=some_wrong_value", headers=headers)
        )
        self.assertEqual(
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
        self.assertDictEqual({k: int(v) for k, v in six.iteritems(get)}, expected)

        logging.info("Testing keywords with GET and no default")
        get = self._simulate(
            "GET", url,
            query_string="arg=1&c=3&d=4",
        )
        self.assertDictEqual({k: int(v) for k, v in six.iteritems(get)}, expected_no_default)

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

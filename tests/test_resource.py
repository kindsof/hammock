from __future__ import absolute_import
import tests.base as base
import six
import logging
import hammock.common as common
import hammock.types as types
import tests.resources1.keywords as keywords


class TestResource(base.TestBase):

    def test_dict(self):
        self.assertDictEqual({'key': 'a', 'value': 1}, self._simulate('POST', '/dict/a', body={'value': 1}))
        self.assertDictEqual({'key': 'b', 'value': 2}, self._simulate('POST', '/dict/b', body={'value': 2}))
        self.assert_status(400, 'POST', '/dict/a', body={'value': 10})
        self.assertDictEqual({'key': 'a', 'value': 1}, self._simulate('GET', '/dict/a'))
        self.assertDictEqual({'key': 'b', 'value': 2}, self._simulate('GET', '/dict/b'))
        self.assertDictEqual({'key': 'a', 'value': 1}, self._simulate('PUT', '/dict/a', body={'value': 10}))
        self.assertDictEqual({'key': 'a', 'value': 10}, self._simulate('GET', '/dict/a'))
        self.assertDictEqual({'key': 'a', 'value': 10}, self._simulate('DELETE', '/dict/a'))
        self.assert_status(404, 'DELETE', '/dict/a')
        self.assert_status(404, 'GET', '/dict/a')
        self.assert_status(404, 'PUT', '/dict/a', body={'value': '1'})
        self.simulate_request('/dict/a', method='POST', body='', headers={common.CONTENT_TYPE: common.TYPE_JSON})
        self.assertEqual('400', self.srmock.status)

    def test_text(self):
        self.assertEqual("HELLO", self._simulate("GET", "/text/upper/hello"))
        self.assertEqual("helly", self._simulate("GET", "/text/replace/hello", query_string="old=o&new=y"))
        self.assertEqual("helly", self._simulate("GET", "/text/replace2/hello", query_string="old=o&new=y"))
        self.assertEqual("hallo", self._simulate("PUT", "/text/replace/hello", body={"old": "e", "new": "a"}))
        self.assertEqual("hallo", self._simulate("POST", "/text/replace/hello", body={"old": "e", "new": "a"}))
        self.assertEqual("helly", self._simulate("DELETE", "/text/replace/hello", query_string="old=o&new=y"))

    def test_sink(self):
        self.assert_status(404, "GET", "/get_something_wrong")
        self.assert_status(404, "GET", "/get_something_wrong/with_query", query_string="a=b")
        self.assert_status(404, "PUT", "/put_something_wrong")
        self.assert_status(404, "PUT", "/put_something_wrong/with_body", body={"value": "1"})
        self.assert_status(404, "POST", "/post_something_wrong")
        self.assert_status(404, "POST", "/post_something_wrong/with_body", body={"value": "1"})
        self.assert_status(404, "delete", "/delete_something_wrong")
        self.assert_status(404, "DELETE", "/delete_something_wrong/with_query", query_string="a=b")

    def test_sub_resource(self):
        self.assertEqual("sub-in-sub1", self._simulate("GET", "/sub-resource/sub"))
        self.assertEqual("sub2-in-sub1", self._simulate("GET", "/sub-resource/sub2"))
        self.assertEqual("sub-in-sub2", self._simulate("GET", "/sub-resource2/sub"))
        self.assertEqual("modified-in-modified", self._simulate("GET", "/different_path/different_sub"))
        self.assertEqual("sub-in-nested-in-sub", self._simulate("GET", "/sub-resource/nested/sub"))

    def test_headers(self):
        headers = {"key1": "value1", "key2": "value2"}
        for key, value in six.iteritems(headers):
            self.assertEqual(
                True,
                self._simulate("GET", "/headers/%s" % key, query_string="value=%s" % value, headers=headers)
            )
        self.assertEqual(
            False,
            self._simulate("GET", "/headers/%s" % next(six.iterkeys(headers)), query_string="value=some_wrong_value", headers=headers)
        )
        self.assertEqual(
            True,
            self._simulate("GET", "/headers/some_wrong_key", query_string="value=None", headers=headers)
        )

    def test_response_headers(self):
        key = 'test'
        headers = {key: 'this'}
        self._simulate('GET', '/headers', headers=headers)
        response_headers = types.Headers(dict(self.srmock.headers))
        self.assertIn(key, response_headers)
        self.assertEqual(headers[key], response_headers[key])

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
        headers = types.Headers(response["headers"])
        self.assertEqual(int(headers["d"]), expected["d"])

    def test_lists(self):
        response = self._simulate('GET', '/lists/3', query_string='argument=1&argument=2')
        self.assertListEqual(response['argument'], [1, 2])
        self.assertEqual(response['path'], 3)
        response = self._simulate('POST', 'lists/3', body=[1, 2])
        self.assertListEqual(response, [1, 2, 3])

    def test_invalid_json_body(self):
        self.simulate_request('/dict/a', method='POST', body='{"value":', headers={common.CONTENT_TYPE: common.TYPE_JSON})
        self.assertEqual('753', self.srmock.status)

    def test_return_values(self):
        self.assertEqual('', self._simulate('GET', '/responses/none'))
        self.assertEqual('string', self._simulate('GET', '/responses/string'))
        self.assertEqual('string', self._simulate('GET', '/responses/string-io'))
        self.assertEqual('bytes', self._simulate('GET', '/responses/bytes'))
        self.assertEqual('bytes', self._simulate('GET', '/responses/bytes-io'))
        self.assertListEqual([1, 2, 3], self._simulate('GET', '/responses/list'))
        expected_string = '<topElem><SubElem1>text1</SubElem1><SubElem2>text2</SubElem2></topElem>'
        self.assertEqual(expected_string, self._simulate('GET', '/responses/xml'))

    def test_patterns(self):
        url = "/patterns"
        self.assertEqual(self._simulate("GET", url), "base")
        self.assertEqual(self._simulate("GET", url + "/123"), "id-123")
        self.assertEqual(self._simulate("GET", url + "/123/extra"), "extra-123")
        self.assertEqual(self._simulate("GET", url + "/123/extra/specific"), "extra-specific-123")

from __future__ import absolute_import

import httplib

import hammock.common as common
import tests.base as base


class TestArgumentTypes(base.TestBase):

    def test_argument_types(self):
        response = self.assert_status(
            httplib.OK,
            common.GET,
            "/argument-types",
            query_string="a_list=1&an_int=1&a_float=0.1&a_bool=True&a_string=123&not_in_doc=123"
        )
        self.assertEqual(response, True)
        response = self.assert_status(
            httplib.OK,
            common.GET,
            "/argument-types",
            query_string="a_list=1&a_list=moshe&an_int=1&a_float=0.1&a_bool=True&a_string=123&not_in_doc=123"
        )
        self.assertEqual(response, True)

        response = self.assert_status(httplib.OK, common.GET, "/argument-types/with-default")
        self.assertEqual(response, True)

        response = self.assert_status(httplib.OK, common.GET, "/argument-types/with-default", query_string="a_bool=False")
        self.assertEqual(response, True)

        # Test no list
        self.assert_status(
            httplib.BAD_REQUEST,
            common.GET,
            "/argument-types",
            query_string="an_int=1&a_float=0.1&a_bool=True&a_string=123&not_in_doc=123"
        )
        # Test bad Int
        self.assert_status(
            httplib.BAD_REQUEST,
            common.GET,
            "/argument-types",
            query_string="a_list=1&an_int=yo&a_float=0.1&a_bool=True&a_string=123&not_in_doc=123"
        )
        # Test bad float
        self.assert_status(
            httplib.BAD_REQUEST,
            common.GET,
            "/argument-types",
            query_string="a_list=1&an_int=1&a_float=yo&a_bool=True&a_string=123&not_in_doc=123"
        )
        # Everything can be a bool
        self.assert_status(
            httplib.OK,
            common.GET,
            "/argument-types",
            query_string="a_list=1&an_int=1&a_float=1.1&a_bool=yo&a_string=123&not_in_doc=123"
        )

    def test_list_conversion(self):
        response = self.assert_status(httplib.OK, common.GET, "/argument-types/to-list", query_string="a_list=1")
        self.assertListEqual(response, ['1'])

        response = self.assert_status(httplib.OK, common.GET, "/argument-types/to-list", query_string="a_list=1&a_list=yo")
        self.assertListEqual(response, ['1', 'yo'])

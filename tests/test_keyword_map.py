from __future__ import absolute_import

import httplib

import hammock
import hammock.common as common
import hammock.exceptions as exceptions
import tests.base as base


class TestKeywordMapping(base.TestBase):

    def test_keyword_mapping(self):
        response = self.assert_status(httplib.OK, common.POST, "/keyword-map", body={"in-valid1": "1", "in-valid2": "2"})
        self.assertEqual(response, {"valid1": "1", "valid2": "2"})

        response = self.assert_status(httplib.OK, common.GET, "/keyword-map", query_string="in-valid1=1&in-valid2=2")
        self.assertEqual(response, {"valid1": "1", "valid2": "2"})

        response = self.assert_status(httplib.OK, common.POST, "/keyword-map", body={"in-valid1": "1"})
        self.assertEqual(response, {"valid1": "1", "valid2": None})

        response = self.assert_status(httplib.OK, common.GET, "/keyword-map", query_string="in-valid1=1")
        self.assertEqual(response, {"valid1": "1", "valid2": None})

    def test_keyword_mapping_negative(self):
        self.assert_status(httplib.BAD_REQUEST, common.POST, "/keyword-map", body={"bad": "1", "in-valid2": "2"})

        # Validate that using python valid arguments but api invalid fails.
        self.assert_status(httplib.BAD_REQUEST, common.POST, "/keyword-map", body={"valid": "1", "valid2": "2"})

    def test_keyword_mapping_validation(self):
        class TestResource(hammock.Resource):
            POLICY_GROUP_NAME = False

            def test_method(self, arg1, arg2):
                pass

        # Validate that mapping an argument that doesnt appear in the method definition fails.
        self.assertRaises(exceptions.BadResourceDefinition, hammock.get(keyword_map={'missing_arg': 'bla'}), TestResource.test_method)

        # Validate that mapping two argument to the same target fails.
        self.assertRaises(exceptions.BadResourceDefinition, hammock.get(keyword_map={'arg1': 'x', 'arg2': 'x'}), TestResource.test_method)

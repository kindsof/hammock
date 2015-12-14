from __future__ import absolute_import
import hammock.exceptions as exceptions
import unittest
import json


class TestExceptions(unittest.TestCase):

    def test_init_and_methods(self):
        internal_server_error = exceptions.InternalServerError('description0')
        self.assertEqual(internal_server_error.status, 500)
        self.assertEqual(internal_server_error.title, 'Internal Server Error')
        self.assertEqual(internal_server_error.description, 'description0')

        bad_request = exceptions.BadRequest('description1')
        bad_request_dict = {'status': 400, 'title': 'Bad Request', 'description': 'description1'}
        self.assertEqual(bad_request.status, bad_request_dict['status'])
        self.assertEqual(bad_request.title, bad_request_dict['title'])
        self.assertEqual(bad_request.description, bad_request_dict['description'])
        self.assertDictEqual(bad_request.to_dict, bad_request_dict)
        self.assertDictEqual(json.loads(bad_request.to_json), bad_request_dict)

import hammock.exceptions as exceptions
import unittest
import json


class TestExceptions(unittest.TestCase):

    def test_init_and_methods(self):
        internal_server_error = exceptions.InternalServerError('description0')
        self.assertEqual(internal_server_error.status, 500)
        self.assertEqual(internal_server_error.title, 'InternalServerError')
        self.assertEqual(internal_server_error.description, 'description0')

        bad_request = exceptions.BadRequest('description1')
        bad_request_dict = {'status': 400, 'title': 'BadRequest', 'description': 'description1'}
        self.assertEqual(bad_request.status, 400)
        self.assertEqual(bad_request.title, 'BadRequest')
        self.assertEqual(bad_request.description, 'description1')
        self.assertDictEqual(bad_request.to_dict, bad_request_dict)
        self.assertDictEqual(json.loads(bad_request.to_json), bad_request_dict)

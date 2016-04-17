from __future__ import absolute_import
import hammock.exceptions as exceptions
import tests.base as base
import tests.resources1.exceptions as exceptions_resource
import ujson as json
import logging


class TestExceptions(base.TestBase):

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

    def test_internal_server_error(self):
        logging.info("Testing for exception raising")

        response = self.assert_status(500, 'GET', '/exceptions/internal')
        self.assertEqual(500, response['status'])
        self.assertEqual('Internal Server Error', response['title'])
        self.assertEqual(repr(Exception(exceptions_resource.DESCRIPTION)), response['description'])

        response = self.assert_status(404, 'GET', '/exceptions/not_found')
        self.assertEqual(404, response['status'])
        self.assertEqual('Not Found', response['title'])
        self.assertEqual(exceptions_resource.DESCRIPTION, response['description'])

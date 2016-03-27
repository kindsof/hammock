from __future__ import absolute_import
import tests.base as base


class TestClientGetRoute(base.TestBase):

    def test_client_get_route(self):
        self.assert_status(200, 'GET', '/_client')

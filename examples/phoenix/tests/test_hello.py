"""Simple resource unittest."""
from __future__ import absolute_import

import tests.base


class HelloTest(tests.base.BaseTest):
    """Tests for 'hello' resource."""

    def test_hello(self):
        """Test hello resource."""
        test_name = 'test' * 200
        query_string = 'name={}'.format(test_name)
        response = self.assert_status(200, 'GET', "/hello", query_string=query_string)
        self.assertDictEqual(response, {'hello': test_name})

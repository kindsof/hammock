from __future__ import absolute_import
import tests.base as base


class TestPatterns(base.TestBase):

    def test_patterns(self):
        url = "/patterns"

        response = self._simulate("GET", url)
        self.assertEqual(response, "base")

        response = self._simulate("GET", url + "/123")
        self.assertEqual(response, "id-123")

        response = self._simulate("GET", url + "/123/extra")
        self.assertEqual(response, "extra-123")
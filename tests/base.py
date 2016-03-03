from __future__ import absolute_import

import os
import hammock.testing as testing


class TestBase(testing.TestBase):

    RESOURCES = 'tests.resources'
    POLICY = os.path.abspath(os.path.join(os.path.dirname(__file__), 'policy.json'))

from __future__ import absolute_import

import os
import hammock.testing as testing


class TestBase(testing.TestBase):

    RESOURCES = 'tests.resources1'
    POLICY = os.path.abspath('tests/policy.json')

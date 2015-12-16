"""Basic resource unittest."""
from __future__ import absolute_import

from hammock.testing import TestBase


class BaseTest(TestBase):
    RESOURCES = 'phoenix.resources'

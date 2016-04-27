from __future__ import absolute_import

import os
import hammock.testing as testing
import hammock.types.credentials as credentials

HEADER_ROLES = "roles"
HEADER_PROJECT_ID = "project-id"
HEADER_USER_NAME = "user-name"


class TestCredentials(credentials.Credentials):
    def __init__(self, headers):
        super(TestCredentials, self).__init__(headers)
        self.roles = headers.get(HEADER_ROLES, '').split(';')
        self.project_id = headers.get(HEADER_PROJECT_ID)
        self.user_name = headers.get(HEADER_USER_NAME)


class TestBase(testing.TestBase):

    RESOURCES = 'tests.resources1'
    POLICY = os.path.abspath('tests/policy.json')

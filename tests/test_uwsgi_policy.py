from __future__ import absolute_import
import requests
import tests.uwsgi_base as uwsgi_base
import tests.base as tests_base


class TestUwsgiPolicy(uwsgi_base.UwsgiBase):

    def test_policy_no_auth_details(self):
        self.assert_not_authorized(self._client.policy.project_admin)
        self.assert_not_authorized(self._client.policy.admin)

    def test_admin(self):
        admin = self.get_client(headers={
            tests_base.HEADER_ROLES: 'admin'
        }, retries=10)
        self.assertEqual(admin.policy.project_admin(), True)
        self.assertEqual(admin.policy.admin(), True)

    def test_project_admin(self):
        project_admin = self.get_client(headers={
            tests_base.HEADER_ROLES: 'project_admin',
            tests_base.HEADER_PROJECT_ID: 'project-id-1'
        }, retries=10)
        self.assertEqual(project_admin.policy.project_admin(project_id='project-id-1'), True)
        self.assert_not_authorized(project_admin.policy.project_admin, project_id='project-id-2')
        self.assert_not_authorized(project_admin.policy.admin, project_id='project-id-1')

    def test_credentials_arg(self):
        username = 'mickmick'
        user = self.get_client(headers={tests_base.HEADER_USER_NAME: username}, retries=10)
        self.assertTrue(user.policy.test_credentials_arg(username))
        self.assertFalse(user.policy.test_credentials_arg('not-me'))
        self.assertTrue(user.policy.test_enforcer_arg(username))
        self.assert_not_authorized(user.policy.test_enforcer_arg, 'not-me')

    def assert_not_authorized(self, func, *args, **kwargs):
        with self.assertRaises(requests.HTTPError) as exc:
            func(*args, **kwargs)
        self.assertEqual(exc.exception.response.status_code, 403)

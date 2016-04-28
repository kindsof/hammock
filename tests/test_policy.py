from __future__ import absolute_import
import os
import unittest

import hammock.policy as _policy
import hammock.exceptions as exceptions
import tests.base as tests_base


POLICY_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'policy_example.json')


class TestPolicy(unittest.TestCase):

    def test_policy(self):

        policy = _policy.Policy(POLICY_FILE)
        self._test_policy(
            policy,
            'project-admin', True,
            {'project_id': 'project-id-1'},
            tests_base.TestCredentials({tests_base.HEADER_ROLES: 'project_admin', tests_base.HEADER_PROJECT_ID: 'project-id-1'})
        )
        self._test_policy(
            policy,
            'project-admin', True,
            {'project_id': 'project-id-2'},
            tests_base.TestCredentials({tests_base.HEADER_ROLES: 'admin', tests_base.HEADER_PROJECT_ID: 'project-id-1'})
        )
        self._test_policy(
            policy,
            'project-admin', False,
            {'project_id': 'project-id-2'},
            tests_base.TestCredentials({tests_base.HEADER_ROLES: 'project_admin', tests_base.HEADER_PROJECT_ID: 'project-id-1'})
        )
        self._test_policy(
            policy,
            'project-admin-list', True,
            {'project_id': 'project-id-1'},
            tests_base.TestCredentials({tests_base.HEADER_ROLES: 'project_admin', tests_base.HEADER_PROJECT_ID: 'project-id-1'})
        )
        self._test_policy(
            policy,
            'project-admin-list', True,
            {'project_id': 'project-id-2'},
            tests_base.TestCredentials({tests_base.HEADER_ROLES: 'admin', tests_base.HEADER_PROJECT_ID: 'project-id-1'})
        )
        self._test_policy(
            policy,
            'project-admin-list', False,
            {'project_id': 'project-id-2'},
            tests_base.TestCredentials({tests_base.HEADER_ROLES: 'project_admin', tests_base.HEADER_PROJECT_ID: 'project-id-1'})
        )

        self._test_policy(policy, 'user-moshe-reference', True, {}, tests_base.TestCredentials({tests_base.HEADER_USER_NAME: 'moshe'}))
        self._test_policy(policy, 'user-moshe-reference', False, {}, tests_base.TestCredentials({tests_base.HEADER_USER_NAME: 'haim'}))

        self._test_policy(policy, 'allow-all', True, {}, {})
        self._test_policy(policy, 'deny-all', False, {}, {})
        self._test_policy(policy, 'rule-does-not-exists', False, {}, {})

    def test_custom_attr(self):

        class CustomClass(dict):
            def __init__(self, headers):
                super(CustomClass, self).__init__(cred_attr=headers['cred-attr'])

        policy = _policy.Policy(POLICY_FILE)
        self._test_policy(policy, 'target-attribute', True, {'target_attr': '1'}, CustomClass({'cred-attr': '1'}))
        self._test_policy(policy, 'target-attribute', False, {'target_attr': '2'}, CustomClass({'cred-attr': '1'}))

    def test_add_rule(self):
        policy = _policy.Policy(POLICY_FILE)

        self._test_policy(policy, 'user-moshe', True, {}, tests_base.TestCredentials({tests_base.HEADER_USER_NAME: 'moshe'}))
        self._test_policy(policy, 'user-haim', False, {}, tests_base.TestCredentials({tests_base.HEADER_USER_NAME: 'haim'}))

        policy.set({'user-haim': 'user_name:haim'})

        self._test_policy(policy, 'user-moshe', True, {}, tests_base.TestCredentials({tests_base.HEADER_USER_NAME: 'moshe'}))
        self._test_policy(policy, 'user-haim', True, {}, tests_base.TestCredentials({tests_base.HEADER_USER_NAME: 'haim'}))

    def test_override_rule(self):
        policy = _policy.Policy(POLICY_FILE)

        self._test_policy(policy, 'user-moshe', True, {}, tests_base.TestCredentials({tests_base.HEADER_USER_NAME: 'moshe'}))
        self._test_policy(policy, 'user-moshe', False, {}, tests_base.TestCredentials({tests_base.HEADER_USER_NAME: 'haim'}))

        policy.set({'user-moshe': 'user_name:haim'})

        self._test_policy(policy, 'user-moshe', False, {}, tests_base.TestCredentials({tests_base.HEADER_USER_NAME: 'moshe'}))
        self._test_policy(policy, 'user-moshe', True, {}, tests_base.TestCredentials({tests_base.HEADER_USER_NAME: 'haim'}))

    def test_project_id_is_none(self):
        policy = _policy.Policy(POLICY_FILE)
        self._test_policy(policy, 'project-none', True, {'project_id': None}, tests_base.TestCredentials({}))
        self._test_policy(policy, 'project-none', False, {'project_id': '1234'}, tests_base.TestCredentials({}))

    @staticmethod
    def _test_policy(policy, rule, allowed, target, credentials):
        msg = 'Failed rule {}: (allowed: {}) target: {}, credentials: {}'.format(rule, allowed, target, credentials)
        try:
            policy.check(rule, target=target, credentials=credentials)
        except exceptions.Forbidden:
            if allowed:
                raise AssertionError(msg)
        else:
            if not allowed:
                raise AssertionError(msg)

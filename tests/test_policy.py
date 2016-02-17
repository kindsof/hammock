from __future__ import absolute_import
import os
import unittest

import hammock.policy as _policy
import hammock.types.headers as _headers
import hammock.exceptions as exceptions
import hammock.common as common


POLICY_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'policy_example.json')


class TestPolicy(unittest.TestCase):

    def test_policy(self):
        policy = _policy.Policy(POLICY_FILE)
        self._test_policy(
            policy,
            'project-admin', True,
            {'project_id': 'project-id-1'},
            {common.HEADER_ROLES: 'project_admin', common.HEADER_PROJECT_ID: 'project-id-1'}
        )
        self._test_policy(
            policy,
            'project-admin', True,
            {'project_id': 'project-id-2'},
            {common.HEADER_ROLES: 'admin', common.HEADER_PROJECT_ID: 'project-id-1'}
        )
        self._test_policy(
            policy,
            'project-admin', False,
            {'project_id': 'project-id-2'},
            {common.HEADER_ROLES: 'project_admin', common.HEADER_PROJECT_ID: 'project-id-1'}
        )
        self._test_policy(
            policy,
            'project-admin-list', True,
            {'project_id': 'project-id-1'},
            {common.HEADER_ROLES: 'project_admin', common.HEADER_PROJECT_ID: 'project-id-1'}
        )
        self._test_policy(
            policy,
            'project-admin-list', True,
            {'project_id': 'project-id-2'},
            {common.HEADER_ROLES: 'admin', common.HEADER_PROJECT_ID: 'project-id-1'}
        )
        self._test_policy(
            policy,
            'project-admin-list', False,
            {'project_id': 'project-id-2'},
            {common.HEADER_ROLES: 'project_admin', common.HEADER_PROJECT_ID: 'project-id-1'}
        )

        self._test_policy(policy, 'user-moshe-reference', True, {}, {common.HEADER_USER_NAME: 'moshe'})
        self._test_policy(policy, 'user-moshe-reference', False, {}, {common.HEADER_USER_NAME: 'haim'})

        self._test_policy(policy, 'allow-all', True, {}, {})
        self._test_policy(policy, 'deny-all', False, {}, {})
        self._test_policy(policy, 'rule-does-not-exists', False, {}, {})

    def test_custom_attr(self):

        class CustomClass(dict):
            def __init__(self, headers):
                super(CustomClass, self).__init__(cred_attr=headers['cred-attr'])

        policy = _policy.Policy(POLICY_FILE, credentials_class=CustomClass)
        self._test_policy(policy, 'target-attribute', True, {'target_attr': '1'}, {'cred-attr': '1'})
        self._test_policy(policy, 'target-attribute', False, {'target_attr': '2'}, {'cred-attr': '1'})

    def test_add_rule(self):
        policy = _policy.Policy(POLICY_FILE)

        self._test_policy(policy, 'user-moshe', True, {}, {common.HEADER_USER_NAME: 'moshe'})
        self._test_policy(policy, 'user-haim', False, {}, {common.HEADER_USER_NAME: 'haim'})

        policy.set({'user-haim': 'user_name:haim'})

        self._test_policy(policy, 'user-moshe', True, {}, {common.HEADER_USER_NAME: 'moshe'})
        self._test_policy(policy, 'user-haim', True, {}, {common.HEADER_USER_NAME: 'haim'})

    def test_override_rule(self):
        policy = _policy.Policy(POLICY_FILE)

        self._test_policy(policy, 'user-moshe', True, {}, {common.HEADER_USER_NAME: 'moshe'})
        self._test_policy(policy, 'user-moshe', False, {}, {common.HEADER_USER_NAME: 'haim'})

        policy.set({'user-moshe': 'user_name:haim'})

        self._test_policy(policy, 'user-moshe', False, {}, {common.HEADER_USER_NAME: 'moshe'})
        self._test_policy(policy, 'user-moshe', True, {}, {common.HEADER_USER_NAME: 'haim'})

    def test_project_id_is_none(self):
        policy = _policy.Policy(POLICY_FILE)
        self._test_policy(policy, 'project-none', True, {'project_id': None}, {})
        self._test_policy(policy, 'project-none', False, {'project_id': '1234'}, {})

    def _test_policy(self, policy, rule, allowed, target, headers):
        msg = 'Failed rule {}: (allowed: {}) target: {}, headers: {}'.format(rule, allowed, target, headers)
        try:
            policy.check(rule, target=target, headers=_headers.Headers(headers))
        except exceptions.Forbidden:
            if allowed:
                raise AssertionError(msg)
        else:
            if not allowed:
                raise AssertionError(msg)

from __future__ import absolute_import
import logging
import os
from oslo_policy import policy
from oslo_policy import opts
import oslo_config.cfg as cfg

import hammock.exceptions as exceptions

LOG = logging.getLogger(__name__)


class Policy(object):
    """
    Define routing policies using a policy json file.
    A policy rule is according to oslo.policy.
    A rule has a name and a boolean expression that is evaluated using the
    headers and target resource parameters.
    - The headers are converted to a credentials dict, by default using hammock.types.Credentials,
      but can be customized using credentials_class parameter.
    - The request is converted to a dict using hammock engine, and passed to oslo.policy as
      the target field.
    - Evaluating the expression:
      The expression is key:value tuple, The key might be:
      * rule: then the target is reference to another rule.
      * role: then the value is looked up in a list stored in a key 'roles' in the credentials dict.
      * other: the key is searched in the credentials rules, and then the value is compared after
        evaluating the python expression: value % target
        Example:
        rule is 'credentials_entry:%(target_entry)s', then
        if credentials are {'credentials_entry': 'x'} and target is {'target_entry': 'x'},
        then the rule is evaluated to True.
    - The expression might have and/or parentheses.
    """

    def __init__(self, policy_file=None):
        """
        :param policy_file: path to a policy json file
        """
        self._policy_file = policy_file
        conf = self._get_conf()
        self._enforcer = policy.Enforcer(conf, use_conf=policy_file is not None)
        self._enforcer.load_rules()
        LOG.info('Policy is loaded with rules: %s', self._enforcer.rules)

    def check(self, rule, target, credentials):
        # Default behavior, when no policy file was loaded or no rules were set,
        # is to approve all checks.
        if self.is_disabled:
            return

        # If any policy was set, the default behavior for undefined rule, is to reject.
        LOG.debug('Checking rule %s on target %s with credentials %s', rule, target, credentials)

        def enforce_func(target):
            # Set None in project_id in case the target don't have one,
            # For all the rules that check for project_id.
            check_target = target.copy()
            check_target.setdefault('project_id', None)
            return self._enforcer.enforce(
                rule=rule, creds=credentials, target=check_target,
                do_raise=True, exc=exceptions.Forbidden
            )

        enforce_func(target)
        return enforce_func

    def set(self, rules_dict):
        LOG.info('Adding rules to policy: %s', rules_dict)
        self._enforcer.set_rules(policy.Rules.from_dict(rules_dict), overwrite=False)

    @property
    def is_disabled(self):
        return self._policy_file is None and not self._enforcer.rules

    @property
    def rules(self):
        self._enforcer.load_rules()
        return self._enforcer.rules

    def _get_conf(self):
        conf = cfg.CONF
        opts.set_defaults(conf, policy_file=self._policy_file)
        if self._policy_file:
            LOG.info('Using policy config file: %s', self._policy_file)
            conf(args=['--config-dir', os.path.dirname(self._policy_file)])
        return conf

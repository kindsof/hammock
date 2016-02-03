from __future__ import absolute_import
import hammock


class Policy(hammock.Resource):
    """
    Tests policy behavior
    the rule_name are listed in tests/policy.json
    """

    @hammock.get('project_admin', rule_name='project-admin')
    def project_admin(self, project_id=None):  # pylint: disable=unused-argument
        return True

    @hammock.get('admin', rule_name='admin')
    def admin(self, project_id=None):  # pylint: disable=unused-argument
        return True

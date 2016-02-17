from __future__ import absolute_import
import hammock


class Policy(hammock.Resource):
    """
    Tests policy behavior
    the rule_name are listed in tests/policy.json
    """

    POLICY_GROUP_NAME = 'policy-override'

    @hammock.get('project_admin', rule_name='project-admin')
    def project_admin(self, project_id=None):  # pylint: disable=unused-argument
        return True

    @hammock.get('admin', rule_name='admin')
    def admin(self, project_id=None):  # pylint: disable=unused-argument
        return True

    @hammock.get('test-credentials-arg')
    def test_credentials_arg(self, username, _credentials):  # pylint: disable=unused-argument
        return username == _credentials['user_name']

class vm_manager: pass
import hammock.exceptions as exceptions

class Vms(hammock.Resource):

   @hammock.get()
   def get(self, _credentials, vm_id):
        vm = vm_manager.get(vm_id)
        if vm['project_id'] != _credentials['project_id']:
            raise exceptions.Unauthorized('Get vm {}'.format(vm_id))
        return vm
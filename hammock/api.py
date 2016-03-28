from __future__ import absolute_import
import hammock.resource_node as resource_node
import hammock.backends as backends
import hammock.policy as policy
import hammock.common_resources as common_resources


class Hammock(resource_node.ResourceNode):
    def __init__(
        self, api, resource_package,
        policy_file=None, credentials_class=None,
        **resource_params
    ):

        self._api = api
        self.resource_package = resource_package
        self.policy = policy.Policy(policy_file=policy_file, credentials_class=credentials_class)
        self._backend = backends.get(api)
        self._backend.add_resources(self, resource_package, **resource_params)
        self._backend.add_resources(self, common_resources)

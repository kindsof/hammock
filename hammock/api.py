from __future__ import absolute_import
import hammock.resource_node as resource_node
import hammock.backends as backends
import hammock.policy as policy
import hammock.common_resources as common_resources


class Hammock(object):
    def __init__(
        self, api, resource_package,
        policy_file=None, credentials_class=None,
        **resource_params
    ):
        self._backend = backends.get(api)
        self._policy = policy.Policy(policy_file=policy_file)
        self._resources = resource_node.ResourceNode()
        resource_params.update({
            '_policy': self._policy,
            '_resource_package': resource_package,
            '_credentials_class': credentials_class,
        })
        self._backend.add_resources(self._resources, resource_package, **resource_params)
        self._backend.add_resources(self._resources, common_resources, **resource_params)

    @property
    def api(self):
        return self._backend.api

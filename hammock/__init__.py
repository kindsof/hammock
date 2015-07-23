import hammock.resource_node as resource_node
import pkgutil


class Hammock(resource_node.ResourceNode):

    def __init__(self, api, resource_package):
        self._api = api
        iter_modules(resource_package, self._add_resource)

    def _add_resource(self, package, module_name, parents):
        prefix = "/".join(parents)
        resource = resource_class(package, module_name)(self._api, prefix)
        node = self
        for parent in parents:
            node = node.add(parent)
        node.add(resource.name(), resource)


def iter_modules(package, callback, parents=None):
    parents = parents or []
    for _, name, ispkg in pkgutil.iter_modules(package.__path__):
        if ispkg:
            package_parents = parents[:]
            son_package = __import__(".".join([package.__name__, name]), fromlist=[package.__name__])
            name = getattr(son_package, "PATH", name)
            package_parents.append(name)
            iter_modules(son_package, callback, package_parents)
        else:
            callback(package, name, parents)


def resource_class(package, module_name):
    module = __import__(".".join([package.__name__, module_name]), fromlist=[package.__name__])
    return getattr(module, module_name.capitalize())

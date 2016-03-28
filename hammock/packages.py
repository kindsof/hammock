from __future__ import absolute_import
import pkgutil
import inspect
import hammock
import collections
import hammock.names as names


Package = collections.namedtuple('Package', ['name', 'path', 'class_name', 'cli_command_name'])


def iter_resource_classes(package):
    """
    Iterate recursively over all classes inherit from hammock.hammock.Resource in the package.
    :param package: package to iterate over
    :return: a list of tuples: (
        resource_class: a resource class
        parents: list of packages names the the module exists in.
    )
    """
    for module, parents in iter_modules(package):
        for resource_class in _iter_resource_classes(module):
            yield resource_class, parents


def iter_modules(package):
    """
    Iterates recursively the package's modules
    :param package: a package to iterate over
    :return: a list of tuples: (
        module: module object,
        parents: list of packages names the the module exists in.
    )
    """
    return _rec_iter_modules(package)


def _rec_iter_modules(package, parents=None):
    modules = []
    parents = parents or []
    for _, name, is_package in pkgutil.iter_modules(package.__path__):
        if is_package:
            # name is package name
            package_parents = parents[:]
            son_package = __import__(".".join([package.__name__, name]))
            path = getattr(son_package, "PATH", name)
            class_name = names.to_class_name(path)
            path_name = getattr(son_package, "PATH", names.to_path(path))
            cli_command_name = getattr(son_package, "CLI_COMMAND_NAME", names.to_command(path))
            package_parents.append(Package(name=name, path=path_name, class_name=class_name, cli_command_name=cli_command_name))
            modules.extend(_rec_iter_modules(son_package, package_parents))
        else:
            # name is module name
            module = __import__(".".join([package.__name__, name]))
            modules.append((module, parents))
    return modules


def _iter_resource_classes(module):
    return [
        getattr(module, attr)
        for attr in dir(module)
        if _is_resource_class(getattr(module, attr))
    ]


def _is_resource_class(obj):
    return inspect.isclass(obj) and issubclass(obj, hammock.Resource)

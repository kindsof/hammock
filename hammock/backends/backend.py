from __future__ import absolute_import
import hammock.packages as packages
import hammock.exceptions as exceptions


class Backend(object):

    def __init__(self, api):
        self._api = api
        self.add_error_handler(exceptions.HttpError, self._api)

    def add_resources(self, base_node, resource_package):
        """
        :param base_node: a resource node to add package resources to
        :param resource_package: resources package
        """
        for resource_class, parents in packages.iter_resource_classes(resource_package):
            prefix = '/'.join(parents)
            node = base_node.get_node(parents)
            node.add(resource_class.name(), resource_class)
            resource = resource_class()
            self.add_route_methods(resource, prefix)
            self.add_sink_methods(resource, prefix)

    def add_route_methods(self, resource, base_path):
        raise NotImplementedError()

    def add_sink_methods(self, resource, base_path):
        raise NotImplementedError()

    def add_error_handler(self, exc_class, api):
        raise NotImplementedError()

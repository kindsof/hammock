from __future__ import absolute_import
import abc

import six

import hammock.packages as packages
import hammock.exceptions as exceptions
import hammock.common as common


class Backend(object):

    def __init__(self, api):
        self._api = api
        self.add_error_handler(exceptions.HttpError, self._api)

    def add_resources(self, api, resource_package, **resource_params):
        """
        :param api: a resource node to add package resources to
        :param resource_package: resources package
        """
        for resource_class, parents in packages.iter_resource_classes(resource_package):
            prefix = '/'.join([parent.path for parent in parents])
            node = api.get_node([parent.name for parent in parents])
            node.add(resource_class.name(), resource_class)
            resource = resource_class(api, None, **resource_params)  # XXX: temporary 2nd argument None, remove them when sagittarius is fixed
            self._add_route_methods(resource, prefix)
            self._add_sink_methods(resource, prefix)

    def _add_route_methods(self, resource, base_path):
        """Add route methods of a resource
        :param resource: a Resource class
        :param base_path: path of resource mounting
        """
        for route_path, methods_map in six.iteritems(resource.routes):
            path = '/' + common.url_join(base_path, route_path)
            self.add_route(path, methods_map)

    def _add_sink_methods(self, resource, base_path):
        """Add sink methods of a resource.
        :param resource: a Resource class
        :param base_path: path of resource mounting
        """
        for sink_path, responder in resource.sinks:
            path = '/' + common.url_join(base_path, sink_path)
            self.add_sink(path, responder)

    @abc.abstractmethod
    def add_route(self, path, methods_map):
        """ Add routes on a specific path
        :param path: url of routing
        :param methods_map: a map of {mathod: responder)
        """

    @abc.abstractmethod
    def add_sink(self, path, responder):
        """ Add sink to path, the sink catches all url with tha path prefix and any method.
        :param path: url of routing
        :param responder: a responder for this url prefix
        """

    @abc.abstractmethod
    def add_error_handler(self, exc_class, api):
        """Add error handler for exception of class exc_class
        :param exc_class: type of exception
        :param api: api instance
        """

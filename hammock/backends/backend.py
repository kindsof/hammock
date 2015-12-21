from __future__ import absolute_import
import abc
import six
import functools
import hammock.packages as packages
import hammock.exceptions as exceptions
import hammock.common as common


class Backend(object):

    LONGEST_SINK_FIRST = True

    def __init__(self, api):
        self.api = api
        self.add_error_handler(exceptions.HttpError, self.api)

    def add_resources(self, base_node, resource_package):
        """
        Add route and sinks methods to the api,
        Iterate over the resources of the resource package,
        and over all sink and route methods in each resource.
        Use backend override methods to add the route or sink to the api.
        :param base_node: a resource node to add package resources to
        :param resource_package: resources package
        """
        sinks = {}  # A mapping of sinks, {path: responder}
        for resource_class, parents in packages.iter_resource_classes(resource_package):
            prefix = '/'.join(parents)
            node = base_node.get_node(parents)
            node.add(resource_class.name(), resource_class)
            resource = resource_class()
            self._add_route_methods(resource, prefix)
            # Collect all sinks from all resource classes
            # add them only after all routes methods were added.
            sinks.update(self._get_sink_methods(resource, prefix))
        # Add the route methods.
        self._add_all_sink_methods(sinks)

    def _add_route_methods(self, resource, base_path):
        """Add route methods of a resource
        :param resource: a Resource class
        :param base_path: path of resource mounting
        """
        for route_path, methods_map in six.iteritems(resource.routes):
            path = '/' + common.url_join(base_path, route_path)
            self.add_route(path, methods_map)

    @staticmethod
    def _get_sink_methods(resource, base_path):
        """
        :param resource: a Resource class
        :param base_path: path of resource mounting
        :return: a dict {path: responder}
        """
        return {
            '/' + common.url_join(base_path, sink_path): responder
            for sink_path, responder in resource.sinks
        }

    def _add_all_sink_methods(self, sinks):
        """
        Add all sinks collected from all resources
        :param sinks: a dict of {path: responder}
        """
        # Iterate over the sinks, sorted with path length, according to self.LONGEST_SINK_FIRST
        sinks = sorted(
            six.iteritems(sinks),
            key=functools.cmp_to_key(lambda v1, v2: len(v1[0]) - len(v2[0])),
            reverse=self.LONGEST_SINK_FIRST,
        )
        for path, responder in sinks:
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

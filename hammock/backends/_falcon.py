from __future__ import absolute_import
import six
import functools
import collections
import re
import logging
import hammock.packages as packages
import hammock.common as common
import hammock.exceptions as exceptions


LOG = logging.getLogger(__name__)


class Falcon(object):

    def __init__(self, api):
        self._api = api
        self._api.add_error_handler(exceptions.HttpError, self._handle_http_error)

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
            self._add_route_methods(resource, prefix)
            self._add_sink_methods(resource, prefix)

    def _add_route_methods(self, resource, base_path):
        paths = collections.defaultdict(dict)
        for method in common.iter_route_methods(resource):
            falcon_method = 'on_{}'.format(method.method.lower())
            paths[method.path][falcon_method] = functools.partial(method.responder, resource)
        for route_path, methods in six.iteritems(paths):
            new_route_class = type(
                self._falcon_class_name(base_path, resource, route_path),
                (),
                methods
            )
            full_path = "/%s" % common.url_join(base_path, resource.name(), route_path)
            self._api.add_route(full_path, new_route_class())
            LOG.debug("Added route %s", full_path)

    def _add_sink_methods(self, resource, base_path):
        sinks = {}
        for method in common.iter_sink_methods(resource):
            full_path = '/' + common.url_join(base_path, resource.name(), method.path)
            pattern = re.compile(common.CONVERT_PATH_VARIABLES(full_path))
            sinks[pattern] = method.method
        for pattern in sorted(sinks, key=functools.cmp_to_key(lambda p1, p2: len(p1.pattern) - len(p2.pattern))):
            self._api.add_sink(functools.partial(sinks[pattern], resource), pattern)
            LOG.debug("Added sink %s for %s", pattern.pattern, repr(sinks[pattern].__code__))

    @staticmethod
    def _falcon_class_name(base_path, resource, route_path):
        return ''.join(
            part.capitalize()
            for part in [
                "Resource",
                common.PATH_TO_NAME(base_path),
                resource.name(),
                common.PATH_TO_NAME(route_path),
            ]
        )

    @staticmethod
    def _handle_http_error(exc, request, response, params):  # pylint: disable=unused-argument
        response.status = str(exc.status)
        response.body = exc.to_json
        response.content_type = common.TYPE_JSON

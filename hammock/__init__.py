from __future__ import absolute_import
import hammock.resource_node as resource_node
import hammock.exceptions as exceptions
import hammock.common as common
import hammock.packages as packages


class Hammock(resource_node.ResourceNode):

    def __init__(self, api, resource_package):
        self._api = api
        self._add_resources(resource_package)
        self._api.add_error_handler(exceptions.HttpError, self._handle_http_error)

    def _add_resources(self, resource_package):
        for resource_class, parents in packages.iter_resource_classes(resource_package):
            prefix = '/'.join(parents)
            resource_class(self._api, prefix)
            node = self._get_node(parents)
            node.add(resource_class.name(), resource_class)

    @staticmethod
    def _handle_http_error(exc, request, response, params):  # pylint: disable=unused-argument
        response.status = str(exc.status)
        response.body = exc.to_json
        response.content_type = common.TYPE_JSON

from __future__ import absolute_import
import six
import functools
import collections
import re
import logging
import hammock.common as common
import hammock.types.request as request
from . import backend

LOG = logging.getLogger(__name__)


class Falcon(backend.Backend):

    def _add_route_methods(self, resource, base_path):
        paths = collections.defaultdict(dict)
        for route_method in common.iter_route_methods(resource):
            falcon_method = 'on_{}'.format(route_method.method.lower())
            paths[route_method.path][falcon_method] = self._responder(resource, route_method.responder)
        for route_path, methods in six.iteritems(paths):
            self._add_route(base_path, resource.name(), route_path, methods)

    def _add_sink_methods(self, resource, base_path):
        sinks = {}
        for method in common.iter_sink_methods(resource):
            full_path = '/' + common.url_join(base_path, resource.name(), method.path)
            pattern = re.compile(common.CONVERT_PATH_VARIABLES(full_path))
            sinks[pattern] = method.responder

        # add the sinks sorted, so sinks with longer url will be queried first.
        for pattern in self._sort_sinks(sinks):
            self._api.add_sink(self._responder(resource, sinks[pattern]), pattern)
            LOG.debug("Added sink %s for %s", pattern.pattern, repr(sinks[pattern].__code__))

    def _responder(self, resource, route_method):
        # This is how falcon calls a resource method,
        # Here we call the inner hammock 'route_method' and update the falcon response.
        def falcon_method(_resource, backend_req, backend_resp, **url_params):
            req = self._req_from_backend(backend_req, url_params)
            resp = route_method(_resource, req)
            self._update_backend_response(resp, backend_resp)
        return functools.partial(falcon_method, resource)

    @staticmethod
    def _req_from_backend(backend_req, url_params):
        return request.Request(
            backend_req.method, backend_req.url, backend_req.headers, backend_req.stream, url_params)

    @staticmethod
    def _update_backend_response(resp, backend_resp):
        backend_resp.status = resp.status
        for key, value in six.iteritems(resp.headers):
            backend_resp.set_header(key, value)
        if hasattr(resp.content, 'read'):
            backend_resp.stream = resp.content
        else:
            backend_resp.body = resp.content

    def _add_route(self, base_path, resource_name, route_path, methods):
        new_route_class = self._get_route_class(base_path, resource_name, route_path, methods)
        full_path = "/%s" % common.url_join(base_path, resource_name, route_path)
        self._api.add_route(full_path, new_route_class())
        LOG.debug('Added route %s', full_path)

    @staticmethod
    def _get_route_class(base_path, resource_name, route_path, methods):
        return type(
            Falcon._falcon_class_name(base_path, resource_name, route_path),
            (),
            methods
        )

    @staticmethod
    def _falcon_class_name(base_path, resource_name, route_path):
        return ''.join(
            part.capitalize()
            for part in [
                'Resource',
                common.PATH_TO_NAME(base_path),
                resource_name,
                common.PATH_TO_NAME(route_path),
            ]
        )

    @staticmethod
    def _handle_http_error(exc, backend_req, backend_resp, url_params):  # pylint: disable=unused-argument
        backend_resp.status = str(exc.status)
        backend_resp.body = exc.to_json
        backend_resp.content_type = common.TYPE_JSON

    @staticmethod
    def _sort_sinks(sinks):
        return sorted(sinks, key=functools.cmp_to_key(lambda p1, p2: len(p1.pattern) - len(p2.pattern)))

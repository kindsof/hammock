from __future__ import absolute_import
import six
import functools
import re
import logging
import hammock.common as common
import hammock.types.request as request
from . import backend

LOG = logging.getLogger(__name__)


class Falcon(backend.Backend):

    def add_route_methods(self, resource, base_path):
        for route_path, methods in six.iteritems(resource.routes):
            methods = {
                'on_' + method.lower(): self._responder(resource, responder)
                for method, responder in six.iteritems(methods)
            }
            self._add_route(base_path, route_path, methods)

    def add_sink_methods(self, resource, base_path):
        for sink_path, responder in resource.sinks:
            full_path = '/' + common.url_join(base_path, sink_path)
            pattern = re.compile(common.CONVERT_PATH_VARIABLES(full_path))
            self._api.add_sink(self._responder(resource, responder), pattern)
            LOG.debug('Added sink %s for %s', pattern.pattern, repr(responder))

    def add_error_handler(self, exc_class, api):
        api.add_error_handler(exc_class, self._handle_http_error)

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

    def _add_route(self, base_path, route_path, methods):
        new_route_class = self._get_route_class(base_path, route_path, methods)
        full_path = '/' + common.url_join(base_path, route_path)
        self._api.add_route(full_path, new_route_class())
        LOG.debug('Added route %s', full_path)

    @staticmethod
    def _get_route_class(base_path, route_path, methods):
        return type(
            Falcon._falcon_class_name(base_path, route_path),
            (),
            methods
        )

    @staticmethod
    def _falcon_class_name(base_path, route_path):
        return ''.join(
            part.capitalize()
            for part in ['Resource', common.PATH_TO_NAME(base_path), common.PATH_TO_NAME(route_path)]
        )

    @staticmethod
    def _handle_http_error(exc, backend_req, backend_resp, url_params):  # pylint: disable=unused-argument
        backend_resp.status = str(exc.status)
        backend_resp.body = exc.to_json
        backend_resp.content_type = common.TYPE_JSON

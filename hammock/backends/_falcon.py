from __future__ import absolute_import
import six
import re
import logging
import hammock.common as common
import hammock.names as names
import hammock.types.request as request
from . import backend

LOG = logging.getLogger(__name__)


class Falcon(backend.Backend):

    def add_route(self, path, methods_map):
        methods = {
            'on_' + method.lower(): staticmethod(self._responder(responder))
            for method, responder in six.iteritems(methods_map)
        }
        new_route_class = self._get_route_class(path, methods)
        self.api.add_route(path, new_route_class())
        for method in six.iterkeys(methods_map):
            LOG.debug('Added route %s %s', method, path)

    def add_sink(self, path, responder):
        pattern = re.compile(names.CONVERT_PATH_VARIABLES(path))
        self.api.add_sink(self._responder(responder), pattern)
        LOG.debug('Added sink %s', path)

    def add_error_handler(self, exc_class, api):
        api.add_error_handler(exc_class, self._handle_http_error)

    def _responder(self, responder):
        # This is how falcon calls a resource method,
        # Here we call the inner hammock 'route_method' and update the falcon response.
        def falcon_method(backend_req, backend_resp, **url_params):
            req = self._req_from_backend(backend_req, url_params)
            resp = responder(req)
            self._update_backend_response(resp, backend_resp)

        return falcon_method

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

    @staticmethod
    def _get_route_class(path, methods):
        return type(Falcon._falcon_class_name(path), (), methods)

    @staticmethod
    def _falcon_class_name(path):
        return 'Resource' + names.to_class_name(path)

    @staticmethod
    def _handle_http_error(exc, backend_req, backend_resp, url_params):  # pylint: disable=unused-argument
        backend_resp.status = str(exc.status)
        backend_resp.body = exc.to_json
        backend_resp.content_type = common.TYPE_JSON

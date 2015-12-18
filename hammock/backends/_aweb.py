from __future__ import absolute_import
import re
import six.moves.urllib as urllib  # pylint: disable=import-error
import functools
import six
import logging
from hammock.types import request
import hammock.common as common
from . import backend
try:
    import aiohttp.web as aweb  # pylint: disable=import-error
except ImportError:
    pass


LOG = logging.getLogger(__name__)


class AWeb(backend.Backend):

    def add_route_methods(self, resource, base_path):
        for route_path, methods in six.iteritems(resource.routes):
            path = '/' + common.url_join(base_path, route_path)
            for method, responder in six.iteritems(methods):
                self._api.add_route(method, path, self._responder(resource, responder))
                LOG.debug('Added route %s %s', method, path)

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
        def web_handler(_resource, backend_req):
            req = self._from_backend_req(backend_req)
            resp = route_method(_resource, req)
            return self._to_backend_resp(resp)
        return functools.partial(web_handler, resource)

    @staticmethod
    def _from_backend_req(backend_req):
        return request.Request(
            method=backend_req.method,
            url=urllib.parse.unparse(backend_req.scheme, backend_req.host, backend_req.path, backend_req.query_string),
            headers=backend_req.headers,
            stream=backend_req.content if backend_req.has_body else None,
            url_params=backend_req.match_info,
        )

    @staticmethod
    def _to_backend_resp(resp):
        if resp.is_stream:
            return aweb.StreamResponse(

            )
        else:
            return aweb.Response(
                body=resp.content,
                status=resp.status,
                headers=resp.headers,
            )

    @staticmethod
    def _handle_http_error(req):
        req.release()  # Eat unread part of HTTP BODY if present

from __future__ import absolute_import
import six.moves.urllib as urllib  # pylint: disable=import-error
import six
import logging
from hammock.types import request
from . import backend
try:
    import aiohttp.web as aweb  # pylint: disable=import-error
except ImportError:
    pass


LOG = logging.getLogger(__name__)


class AWeb(backend.Backend):

    def add_route(self, path, methods_map):
        for method, responder in six.iteritems(methods_map):
            self.api.add_route(method, path, self._responder(responder))
            LOG.debug('Added route %s %s', method, path)

    def add_sink(self, path, responder):
        # TODO: add sink
        LOG.debug('Added sink %s', path)

    def add_error_handler(self, exc_class, api):
        api.add_error_handler(exc_class, self._handle_http_error)

    def _responder(self, route_method):
        # This is how falcon calls a resource method,
        # Here we call the inner hammock 'route_method' and update the falcon response.
        def web_handler(backend_req):
            req = self._from_backend_req(backend_req)
            resp = route_method(req)
            return self._to_backend_resp(resp)
        return web_handler

    @staticmethod
    def _from_backend_req(backend_req):
        return request.Request(
            method=backend_req.method,
            url=urllib.parse.unparse(backend_req.scheme, backend_req.host, backend_req.path, backend_req.query_string),
            headers=backend_req.headers,
            content=backend_req.content if backend_req.has_body else None,
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

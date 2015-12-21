from __future__ import absolute_import
import io
import six
import logging
import hammock.types.request as request
import hammock.exceptions as exceptions
import hammock.common as common
from . import backend
import aiohttp.web as aweb  # pylint: disable=import-error


LOG = logging.getLogger(__name__)


class AWeb(backend.Backend):

    def __init__(self, api=None, **kwargs):
        if api is None:
            api = aweb.Application(
                middlewares=[middleware_factory],
                **kwargs
            )
        super(AWeb, self).__init__(api)

    def add_route(self, path, methods_map):
        for method, responder in six.iteritems(methods_map):
            self.api.router.add_route(method, path, self._responder(responder), expect_handler=_not_found)
            LOG.debug('Added route %-6s %s', method, path)

    def add_sink(self, path, responder):
        # Add {_tail:.*} to the end of the path and register it on any method.
        register_path = path + '{{{}:.*}}'.format(common.KW_TAIL)
        self.api.router.add_route('*', register_path, self._responder(responder), expect_handler=_not_found)
        LOG.debug('Added sink         %s', path)

    def add_error_handler(self, exc_class, api):
        # The error handler is added in the middleware in the init of the class.
        pass

    def _responder(self, route_method):
        # This is how falcon calls a resource method,
        # Here we call the inner hammock 'route_method' and update the falcon response.
        def web_handler(backend_req):
            req = self._from_backend_req(backend_req)
            resp = route_method(req)
            return self._to_backend_resp(resp, backend_req)
        return web_handler

    @staticmethod
    def _from_backend_req(backend_req):
        return request.Request(
            method=backend_req.method,
            url=AWeb._backend_url(backend_req),
            headers=backend_req.headers,
            stream=backend_req.content if backend_req.has_body else None,
            url_params=backend_req.match_info,
        )

    @staticmethod
    def _backend_url(backend_req):
        url = '{scheme}://{host}{path}'.format(
            scheme=backend_req.scheme, host=backend_req.host, path=backend_req.path)
        if backend_req.query_string:
            url += '?' + backend_req.query_string
        return url

    @staticmethod
    def _to_backend_resp(resp, backend_req):
        if resp.is_stream:
            backend_resp = aweb.StreamResponse(status=resp.status, headers=resp.headers)
            # Send headers back to client
            backend_resp.start(backend_req)  # .start is the synchronous version of .prepare
            # Send the stream in buffers
            resp.stream.seek(0, io.SEEK_END)
            length = resp.stream.tell()
            resp.stream.seek(0)
            while resp.stream.tell() < length:
                data = resp.stream.read(io.DEFAULT_BUFFER_SIZE)
                if isinstance(data, six.string_types):
                    data = data.encode(common.ENCODING)
                backend_resp.write(data)
            return backend_resp
        else:
            kwargs = dict(status=resp.status, headers=resp.headers)
            if isinstance(resp.content, six.string_types):
                kwargs['text'] = resp.content
            else:
                kwargs['body'] = resp.content
            return aweb.Response(**kwargs)

    @staticmethod
    def _handle_http_error(req):
        req.release()  # Eat unread part of HTTP BODY if present


async def _not_found(request):  # noqa  # pylint: disable=unused-argument
    request.transport.write(b"HTTP/1.1 404 Not Found\r\n\r\n")


async def middleware_factory(app, handler):
    async def cache_exception_handler(req):
        """
        Handler exceptions thrown in handler, convert them into an http response
        """
        try:
            return await handler(req)
        except exceptions.HttpError as exc:
            return aweb.json_response(status=str(exc.status), data=exc.to_dict)

    return cache_exception_handler

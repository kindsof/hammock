import hammock.common as common
import requests
import logging
import urlparse

import collections

Response = collections.namedtuple("Response", ["stream", "headers", "status"])


class Redirect(object):
    PATH = ""
    DEST = ""

    def __init__(self, api):
        logging.info(
            "Added %s redirection: %s to %s",
            self.__class__.__name__, self.PATH, self.DEST)
        api.add_sink(self, self.PATH)

    def __call__(self, request, response):
        logging.info("Processing %s", request.url)
        body_or_stream, response._headers, response.status = self._process(request)
        response.status = str(response.status)
        if hasattr(body_or_stream, "read"):
            response.stream = body_or_stream
        else:
            response.body = body_or_stream

    def _process(self, request):
        """
        Process a request (has path, url, method, stream, headers, etc attributes...)
        Return tuple (body_or_stream, headers, status)
        """
        return self._passthrough(request)

    def _passthrough(self, request):
        redirection_url = common.url_join(self.DEST, self._transform_path(request.path))
        logging.info("Passthrough to %s", redirection_url)
        inner_request = requests.Request(
            request.method,
            url=redirection_url,
            data=request.stream if request.method in ("POST", "PUT", "PATCH") else None,
            headers={
                k: v if k.lower() != "host" else urlparse.urlparse(self.DEST).netloc
                for k, v in request.headers.iteritems()
                if v != ""
            },
        )
        session = requests.Session()
        try:
            prepared = session.prepare_request(inner_request)
            if request.headers.get('CONTENT-LENGTH'):
                prepared.headers['CONTENT-LENGTH'] = request.headers.get('CONTENT-LENGTH')
            if request.headers.get('TRANSFER-ENCODING'):
                del prepared.headers['TRANSFER-ENCODING']

            inner_response = session.send(prepared, stream=True)
            body_or_stream, headers, status = self._process_passthrough_response(
                Response(inner_response.raw, inner_response.headers, str(inner_response.status_code)))
            return body_or_stream, headers, status
        finally:
            session.close()

    def _transform_path(self, path):
        return path[len(self.PATH):]

    def _process_passthrough_response(self, response):
        """
        return a tuple of (body_or_stream, headers, status)
        if body_or_stream is str, it will be the response body, otherwise, it would be a stream
        the body_or_stream as a response
        """
        return response

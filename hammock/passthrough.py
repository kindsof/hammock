from __future__ import absolute_import
import six
import logging
import requests
import hammock.common as common
import hammock.types as types
import hammock.request as request


def passthrough(self, req, response, dest, pre_process, post_process, trim_prefix, func, exception_handler, **params):
    req = request.Request.from_falcon(req)
    logging.debug('[Passthrough received %s] requested: %s', req.uid, req.url)
    try:
        context = {}
        if trim_prefix:
            _trim_prefix(req, trim_prefix)
        if pre_process:
            pre_process(req, context, **params)
        if dest:
            output = send_to(req, dest)
        else:
            output = func(self, req, **params)
        if post_process:
            output = post_process(output, context, **params)
        body_or_stream, response._headers, response.status = output
        response.status = str(response.status)
        if hasattr(body_or_stream, "read"):
            response.stream = body_or_stream
        else:
            response.body = body_or_stream
    except Exception as exc:  # pylint: disable=broad-except
        common.log_exception(exc, req.uid)
        self.handle_exception(exc, exception_handler)
    finally:
        logging.debug(
            '[Passthrough response %s] status: %s, body: %s', req.uid, response.status, response.body,
        )


def send_to(req, dest):
    redirection_url = common.url_join(dest, req.path) + '?' + req.query
    logging.info('[Passthrough %s] redirecting to %s', req.uid, redirection_url)
    inner_request = requests.Request(
        req.method,
        url=redirection_url,
        data=req.stream if req.method not in common.URL_PARAMS_METHODS else None,
        headers={
            k: v if k.lower() != "host" else six.moves.urllib.parse.urlparse(dest).netloc
            for k, v in six.iteritems(req.headers)
            if v != ""
        },
    )
    session = requests.Session()
    try:
        prepared = session.prepare_request(inner_request)
        if req.headers.get(common.CONTENT_LENGTH):
            prepared.headers[common.CONTENT_LENGTH] = req.headers.get(common.CONTENT_LENGTH)
        if req.headers.get('TRANSFER-ENCODING'):
            del prepared.headers['TRANSFER-ENCODING']
        inner_response = session.send(prepared, stream=True)
        return types.Response(inner_response.raw, inner_response.headers, inner_response.status_code)
    finally:
        session.close()


def _trim_prefix(request, trim_prefix):
    request.path = request.path.lstrip("/")[len(trim_prefix.strip("/")):]

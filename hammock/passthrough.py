import logging
import requests
import urlparse
import uuid
import hammock.common as common
import hammock.types as types


def passthrough(self, request, response, dest, pre_process, post_process, trim_prefix, func, **params):
    request_uuid = uuid.uuid4()
    logging.debug("[Passthrough received %s] requested: %s", request_uuid, request.url)
    try:
        context = {}
        if trim_prefix:
            _trim_prefix(request, trim_prefix)
        if pre_process:
            pre_process(request, context, **params)
        if dest:
            output = send_to(request, dest, request_uuid)
        else:
            output = func(self, request, **params)
        if post_process:
            output = post_process(output, context, **params)
        body_or_stream, response._headers, response.status = output
        response.status = str(response.status)
        if hasattr(body_or_stream, "read"):
            response.stream = body_or_stream
        else:
            response.body = body_or_stream
    except Exception as e:
        common.log_exception(e, request_uuid)
        raise
    finally:
        logging.debug(
            "[Passthrough response %s] status: %s, body: %s",
            request_uuid, response.status, response.body,
        )


def send_to(request, dest, request_uuid=None):
    redirection_url = common.url_join(dest, request.relative_uri)
    logging.info("[Passthrough %s] redirecting to %s", request_uuid, redirection_url)
    inner_request = requests.Request(
        request.method,
        url=redirection_url,
        data=request.stream if request.method not in common.URL_PARAMS_METHODS else None,
        headers={
            k: v if k.lower() != "host" else urlparse.urlparse(dest).netloc
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
        return types.Response(inner_response.raw, inner_response.headers, inner_response.status_code)
    finally:
        session.close()


def _trim_prefix(request, trim_prefix):
    request.path = request.path.lstrip("/")[len(trim_prefix.strip("/")):]

import logging
import requests
import urlparse
import hammock.common as common
import hammock.types as types


def passthrough(request, response, dest, pre_process, post_process, trim_prefix, func, **params):
    logging.info("Redirecting %s", request.url)
    if trim_prefix:
        _trim_prefix(request, trim_prefix)
    if pre_process:
        pre_process(request, **params)
    if dest:
        output = _passthrough(request, dest)
    else:
        output = func(request, **params)
    if post_process:
        output = post_process(output, **params)
    body_or_stream, response._headers, response.status = output
    response.status = str(response.status)
    if hasattr(body_or_stream, "read"):
        response.stream = body_or_stream
    else:
        response.body = body_or_stream


def _passthrough(request, dest):
    redirection_url = common.url_join(dest, request.path)
    logging.info("Passthrough to %s", redirection_url)
    inner_request = requests.Request(
        request.method,
        url=redirection_url,
        data=request.stream if request.method in ("POST", "PUT", "PATCH") else None,
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

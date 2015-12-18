from __future__ import absolute_import
import six
import logging
import requests
import hammock.common as common
import hammock.types.response as response


LOG = logging.getLogger(__name__)


def passthrough(resource, req, dest, pre_process, post_process, trim_prefix, func):
    LOG.debug('[Passthrough received %s] requested: %s', req.uid, req.url)
    context = {}
    if trim_prefix:
        req.trim_prefix(trim_prefix)
    if pre_process:
        pre_process(req, context, **req.url_params)

    resp = send_to(req, dest) if dest else func(resource, req, **req.url_params)

    if post_process:
        resp = post_process(resp, context, **req.url_params)  # XXX: should remove the resp = once harbour will adapt
    LOG.debug('[Passthrough response %s] status: %s, body: %s', req.uid, resp.status, resp.content)
    return resp


def send_to(req, dest):
    redirection_url = common.url_join(dest, req.relative_uri)
    LOG.info('[Passthrough %s] redirecting to %s', req.uid, redirection_url)
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
        return response.Response(inner_response.raw, inner_response.headers, inner_response.status_code)
    finally:
        session.close()

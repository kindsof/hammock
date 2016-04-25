from __future__ import absolute_import
import six
import logging
import requests
import hammock.common as common
import hammock.types.response as response


LOG = logging.getLogger(__name__)


def proxy(req, dest):
    redirection_url = common.url_join(dest, req.relative_uri)
    LOG.info('[Proxy %s] to %s', req.uid, redirection_url)
    inner_request = requests.Request(
        req.method,
        url=redirection_url,
        data=req.content if req.method not in common.URL_PARAMS_METHODS else None,
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

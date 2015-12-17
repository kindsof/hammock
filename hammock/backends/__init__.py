# flake8: noqa
# pylint: disable=unused-import

from __future__ import absolute_import
import six
from . import _falcon
from . import _aweb
import hammock.types.request as request
import hammock.types.response as response

try:
    import falcon
except ImportError:
    falcon = None

try:
    import aiohttp.web as aweb
except ImportError:
    aweb = None


def get(api):
    if falcon and isinstance(api, falcon.API):
        return _falcon.Falcon(api)
    elif aweb and isinstance(api, aweb.Application):
        return _aweb.AWeb(api)
    else:
        raise RuntimeError('Invalid API given, or api library not abailable.')


def get_request(backend_req):
    if falcon and isinstance(backend_req, falcon.Request):
        return request.Request(backend_req.method, backend_req.url, backend_req.headers, backend_req.stream)

    elif aweb and isinstance(backend_req, aweb.Request):
        pass

    else:
        raise Exception('Unsupported request type %s', type(backend_req))


def update_response(resp, backend_resp):
    if falcon and isinstance(backend_resp, falcon.Response):
        backend_resp.status = resp.status
        for key, value in six.iteritems(resp.headers):
            backend_resp.set_header(key, value)
        if hasattr(resp.content, 'read'):
            backend_resp.stream = resp.content
        else:
            backend_resp.body = resp.content

    elif aweb and isinstance(backend_resp, aweb.Response):
        pass

    else:
        raise Exception('Unsupported response type %s', type(backend_resp))

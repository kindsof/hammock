# flake8: noqa
# pylint: disable=unused-import

from __future__ import absolute_import
from . import _falcon
from . import _aweb

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
        raise RuntimeError('Invalid API given, or api library not available.')

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


def get(api, **kwargs):
    if falcon and isinstance(api, falcon.API):
        return _falcon.Falcon(api)
    elif falcon and api == 'flacon':
        return _falcon.Falcon(falcon.API())
    elif aweb and api == 'aiohttp':
        return _aweb.AWeb()
    else:
        raise RuntimeError('Invalid API given, or api library not available.')

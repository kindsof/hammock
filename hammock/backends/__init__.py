# flake8: noqa
# pylint: disable=unused-import

from __future__ import absolute_import
import hammock
from . import _falcon
from . import _aweb

try:
    import falcon
except ImportError:
    falcon = None


def get(api, **kwargs):
    if api == hammock.FALCON:
        api = falcon.API(**kwargs)
        return _falcon.Falcon(api)
    elif api == hammock.AWEB:
        import aiohttp.web as aweb  # pylint: disable=import-error
        api = aweb.Application(**kwargs)
        return _aweb.AWeb(api)
    elif falcon and isinstance(api, falcon.API):
        return _falcon.Falcon(api)
    else:
        raise RuntimeError('Invalid API given, or api library not available.')

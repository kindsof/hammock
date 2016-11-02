from __future__ import absolute_import
import hammock.proxy as proxy
import hammock.common as common

from . import wrapper


class Sink(wrapper.Wrapper):

    def _wrapper(self, req):
        kwargs = {}
        credentials = None
        if self.credentials_class and common.KW_CREDENTIALS in self.spec.args:
            credentials = self.credentials_class(req.headers)
            req.url_params[common.KW_CREDENTIALS] = credentials

        if self.dest is None:
            return self(req, **req.url_params)  # pylint: disable=not-callable
        else:
            return proxy.proxy(req, self.dest)


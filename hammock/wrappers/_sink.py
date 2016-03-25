from __future__ import absolute_import
import hammock.proxy as proxy

from . import wrapper


class Sink(wrapper.Wrapper):

    def _wrapper(self, req):
        if self.dest is None:
            return self(req, **req.url_params)  # pylint: disable=not-callable
        else:
            return proxy.proxy(req, self.dest)

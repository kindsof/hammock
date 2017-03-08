from __future__ import absolute_import

import inspect

import hammock.common as common
import hammock.proxy as proxy
from . import wrapper


class Sink(wrapper.Wrapper):

    def _wrapper(self, req):
        if self.dest is not None and not inspect.isgeneratorfunction(self.func):
            # If it's a proxy function, and also not a generator,
            # we have no need in parsing credentials
            return proxy.proxy(req, self.dest)

        if self.credentials_class and common.KW_CREDENTIALS in self.spec.args:
            credentials = self.credentials_class(req.headers)
            req.url_params[common.KW_CREDENTIALS] = credentials

        if self.dest is None:
            return self(req, **req.url_params)  # pylint: disable=not-callable
        else:
            generator = self(req, **req.url_params)
            # code before 'yield'
            next(generator)
            # request itself
            resp = proxy.proxy(req, self.dest)
            try:
                # code after yield
                generator.send(resp)
            except StopIteration:
                # Here the generator ends, everything's good!
                pass
            return resp

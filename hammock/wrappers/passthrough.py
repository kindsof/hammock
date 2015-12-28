from __future__ import absolute_import
from . import wrapper
import hammock.passthrough as passthrough_module


class Passthrough(wrapper.Wrapper):

    dest = None
    pre_process = None
    post_process = None
    trim_prefix = False
    exception_handler = None

    def _wrapper(self, req):
        return passthrough_module.passthrough(
            resource=self._resource,
            req=req,
            dest=self.dest,
            pre_process=self.__class__.pre_process,
            post_process=self.__class__.post_process,
            trim_prefix=self.trim_prefix,
            func=self.func,
        )

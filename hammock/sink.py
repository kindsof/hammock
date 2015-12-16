from __future__ import absolute_import
import hammock.common as common
import hammock.passthrough as passthrough
import functools


def sink(path="", dest=None, pre_process=None, post_process=None, trim_prefix=False, exception_handler=None):
    def _decorator(func):
        func.is_sink = True
        func.path = path
        func.dest = dest
        if func.dest:
            common.func_is_pass(func)

        @functools.wraps(func)
        def _wrapper(self, request, response, **params):
            passthrough.passthrough(
                self,
                request,
                response,
                dest,
                pre_process,
                post_process,
                trim_prefix,
                func,
                exception_handler,
                **params
            )
        func.method = _wrapper
        return func
    return _decorator

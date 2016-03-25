from __future__ import absolute_import
from ._route import Route  # noqa
from ._sink import Sink  # noqa


def route(*args, **kwargs):
    return lambda func: Route(func, *args, **kwargs)


def sink(*args, **kwargs):
    return lambda func: Sink(func, *args, **kwargs)

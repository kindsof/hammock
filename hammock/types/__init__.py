from __future__ import absolute_import

# flake8: noqa
# pylint: disable=unused-import
from . import response as response
from .headers import Headers
from .request import Request
from .file import File


# XXX: temporary workaround, until dependencies will convert stream to content
def Response(stream, headers, status):  # pylint: disable=invalid-name
    return response.Response(stream, headers, status)

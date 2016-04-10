from __future__ import absolute_import
try:
    import ujson as json
except ImportError:
    import json

BAD_REQUEST = 400
UNAUTHORIZED = 401
FORBIDDEN = 403
NOT_FOUND = 404
BAD_METHOD = 405
CONFLICT = 409
OVER_LIMIT = 413
BAD_MEDIA_TYPE = 415
BAD_DATA = 415
INTERNAL_SERVER_ERROR = 500
RESOURCE_NOT_IMPLEMENTED = 501
SERVICE_UNAVAILABLE = 503
MALFORMED_JSON = 753


class HttpError(Exception):
    def __init__(self, status=500, title='InternalServerError', description=''):
        self.status = status
        self.title = title
        self.description = description
        super(HttpError, self).__init__(
            'HTTP {}: {}'.format(status, title))

    @property
    def to_json(self):
        return json.dumps(self.to_dict)

    @property
    def to_dict(self):
        return {'title': self.title, 'description': self.description, 'status': self.status}

    def __str__(self):  # pragma: no cover
        return '<{} {}>(title="{}", description="{}")'.format(
            self.__class__.__name__, self.status, self.title, self.description)

    __repr__ = __str__


def class_factory(status, title, description=''):
    def init(self, description=description):
        HttpError.__init__(self, status, title, description)

    return type(title, (HttpError,), {'__init__': init})


# pylint: disable=invalid-name
BadRequest = class_factory(BAD_REQUEST, 'Bad Request')
Unauthorized = class_factory(UNAUTHORIZED, 'Unauthorized')
Forbidden = class_factory(FORBIDDEN, 'Forbidden')
NotFound = class_factory(NOT_FOUND, 'Not Found')
BadMethod = class_factory(BAD_METHOD, 'Bad Method')
Conflict = class_factory(CONFLICT, 'Conflict')
OverLimit = class_factory(OVER_LIMIT, 'Over Limit')
BadMediaType = class_factory(BAD_MEDIA_TYPE, 'Bad Media Type')
BadData = class_factory(BAD_DATA, 'Bad Data')
InternalServerError = class_factory(INTERNAL_SERVER_ERROR, 'Internal Server Error')
ResourceNotImplemented = class_factory(RESOURCE_NOT_IMPLEMENTED, 'Not Implemented')
ServiceUnavailable = class_factory(SERVICE_UNAVAILABLE, 'Service Unavailable')
MalformedJson = class_factory(MALFORMED_JSON, 'Malformed JSON',
                              'Could not decode the request body. The JSON was incorrect or not encoded as UTF-8.')


class BadResourceDefinition(Exception):
    pass

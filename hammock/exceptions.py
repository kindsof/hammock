from __future__ import absolute_import
import json


class HttpError(Exception):
    def __init__(self, status=500, title='InternalServerError', description=''):
        self.status = status
        self.title = title
        self.description = description
        super(HttpError, self).__init__(
            'HTTP {}: {}'.format(status, title))

    @property
    def to_json(self):
        return json.dumps(self.to_dict, indent=4, sort_keys=True)

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

BadRequest = class_factory(400, 'Bad Request')
Unauthorized = class_factory(401, 'Unauthorized')
Forbidden = class_factory(403, 'Forbidden')
NotFound = class_factory(404, 'Not Found')
BadMethod = class_factory(405, 'Bad Method')
Conflict = class_factory(409, 'Conflict')
OverLimit = class_factory(413, 'Over Limit')
BadMediaType = class_factory(415, 'Bad Media Type')
BadData = class_factory(415, 'Bad Data')
InternalServerError = class_factory(500, 'Internal Server Error')
ResourceNotImplemented = class_factory(501, 'Not Implemented')
ServiceUnavailable = class_factory(503, 'Service Unavailable')
MalformedJson = class_factory(
    753, 'Malformed JSON',
    'Could not decode the request body. The JSON was incorrect or not encoded as UTF-8.')

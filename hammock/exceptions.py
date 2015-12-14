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

    def __str__(self):
        return '<{} {}>(title="{}", description="{}")'.format(
            self.__class__.__name__, self.status, self.title, self.description)

    __repr__ = __str__


def class_factory(status, title):
    def init(self, description):
        return HttpError.__init__(self, status, title, description)

    return type(
        title,
        (HttpError,),
            {
                '__init__': init
            }
    )

BadRequest = class_factory(400, 'BadRequest')
Unauthorized = class_factory(401, 'Unauthorized')
Forbidden = class_factory(403, 'Forbidden')
NotFound = class_factory(404, 'NotFound' )
BadMethod = class_factory(405, 'BadMethod')
Conflict = class_factory(409, 'Conflict')
OverLimit = class_factory(413, 'OverLimit')
BadMediaType = class_factory(415, 'BadMediaType')
InternalServerError = class_factory(500, 'InternalServerError')
NotImplemented = class_factory(501, 'NotImplemented')
ServiceUnavailable = class_factory(503, 'ServiceUnavailable')

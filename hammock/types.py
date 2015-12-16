from __future__ import absolute_import
import six
import inspect
import hammock.response as response
from hammock.headers import Headers  # noqa  # pylint: disable=unused-import


# XXX: temporary workaround, until dependencies will convert stream to content
def Response(stream, headers, status):  # noqa  # pylint: disable=invalid-name
    return response.Response(stream, headers, status)


class File(object):

    def __init__(self, stream, content_length):
        self.stream = stream
        self.content_length = int(content_length)
        self.len = self.content_length

    def __len__(self):
        return self.content_length


class FuncSpec(object):

    def __init__(self, func):
        self.args = []
        self.kwargs = {}
        self.keywords = None
        inspect_method = self._py2_from_func if six.PY2 else self._py3_from_func
        inspect_method(func)

    def _py2_from_func(self, func):
        spec = inspect.getargspec(func)  # pylint: disable=deprecated-method
        defaults = spec.defaults or []
        self.args = spec.args[1:len(spec.args) - len(defaults)]
        keywords = spec.args[len(spec.args) - len(defaults):]
        self.kwargs = dict(six.moves.zip(keywords, defaults))
        self.keywords = spec.keywords

    def _py3_from_func(self, func):
        # pylint: disable=no-member
        parameters = inspect.signature(func).parameters
        for param in parameters.values():
            if param.name == 'self':
                continue
            if param.kind == inspect.Parameter.VAR_KEYWORD:
                self.keywords = param.name
            elif param.default == inspect.Signature.empty:
                self.args.append(param.name)
            else:
                self.kwargs[param.name] = param.default
        # pylint: enable=no-member

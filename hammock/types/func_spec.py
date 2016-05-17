from __future__ import absolute_import
import collections
import inspect
import six
import re
import hammock.types.args as args
import hammock


PARAM_IS_SPECIAL = re.compile(r'^[ ]*:(param|return)')
PARAM_RE = re.compile(r'^[ ]*:param([ ]+(?P<type>[\w\[\]]+))?[ ]+(?P<name>\w+):[ ]*(?P<doc>.*)$', re.MULTILINE)
RETURN_RE = re.compile(r'^[ ]*:return([ ]+(?P<type>\w+))?:[ ]*(?P<doc>.*)$', re.MULTILINE)


class FuncSpec(object):

    def __init__(self, func):
        self._func = func
        self.args = []
        self.kwargs = {}
        self.keywords = None
        self._inspect(func)
        self.doc, doc_args_info, self.returns = self._get_doc_parts(func.__doc__)
        self.all_args = set(self.args) | set(self.kwargs)
        self.args_info = self._collect_args_info(doc_args_info)

    def match_and_convert(self, kwargs):
        """
        Checks if self._func signature matches invocation with kwargs.
        """
        keys = set(kwargs)
        missing = set(self.args) - keys
        not_expected = keys - self.all_args
        if missing:
            raise TypeError('Missing arguments: {}. Expected at least: {}. Got: {}'.format(missing, self.args, kwargs))
        if not self.keywords and not_expected:
            raise TypeError('Got unexpected arguments: {}. Expect: {}. Got: {}.'.format(not_expected, self.all_args, kwargs))
        self._convert_args(kwargs)

    def _collect_args_info(self, doc_args_info):
        # Must be ordered, because of positional arguments.
        args_info = collections.OrderedDict()
        for arg in (self.args + self.kwargs.keys()):
            args_info[arg] = doc_args_info.get(arg, self._get_arg(arg))
        if self.keywords:
            args_info[self.keywords] = self._get_arg(self.keywords)
        return args_info

    def _convert_args(self, kwargs):
        """
        Inplace conversion of the data types according to self.spec
        :param kwargs: keyword arguments supposed to be passed to self.func
        """
        for name, value in six.iteritems(kwargs):
            if name not in self.all_args:
                continue
            arg = self.args_info[name]
            try:
                kwargs[name] = arg.convert(value)
            except ValueError as exc:
                raise hammock.exceptions.BadRequest(
                    "Argument '{}' should be of type {}, got bad value: '{}'. ({})".format(
                        name, arg.type_name, value, exc))

    def _inspect(self, func):
        if six.PY2:
            spec = inspect.getargspec(func)  # pylint: disable=deprecated-method
            defaults = spec.defaults or []
            spec_args = spec.args[:]
            if spec_args[0] == 'self':
                spec_args = spec_args[1:]
            self.args = spec_args[:len(spec_args) - len(defaults)]
            keywords = spec_args[len(spec_args) - len(defaults):]
            self.kwargs = dict(six.moves.zip(keywords, defaults))
            self.keywords = spec.keywords
        elif six.PY3:
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

    def _get_doc_parts(self, doc):
        intro = []
        args_info = {}
        returns = None
        if doc:
            # get func doc
            for line in doc.split('\n'):
                if not PARAM_IS_SPECIAL.match(line):
                    intro.append(line)
                else:
                    break
            intro = '\n'.join(self._trim_leading_spaces(intro))

            # get params
            doc = self._doc_mask_endlines(doc)
            doc = doc.replace('\\n:param', '\n:param').replace('\\n:return', '\n:return')
            for arg_info in PARAM_RE.finditer(doc):
                if arg_info:
                    arg = self._get_arg_from_doc(arg_info)
                    args_info[arg.name] = arg

            # get return
            for returns in RETURN_RE.finditer(doc):
                returns = self._get_arg_from_doc(returns)
                break

        return intro, args_info, returns

    @staticmethod
    def _trim_leading_spaces(lines):
        spaces_count = [len(line) - len(line.lstrip()) for line in lines]
        trim_left = min([count for count in spaces_count if count] or [0])
        if not trim_left:
            lines = [line.lstrip() for line in lines]
        else:
            lines = [line[trim_left:] if line.startswith(' ' * trim_left) else line.lstrip() for line in lines]
        return lines

    @staticmethod
    def _doc_mask_endlines(doc):
        return '\\n'.join((line.strip() for line in doc.split('\n')))

    @staticmethod
    def _doc_return_endlines(doc):
        return doc.replace('\\n', '\n').strip()

    def _get_arg_from_doc(self, match):
        arg = match.groupdict()
        doc = self._doc_return_endlines(arg['doc'])
        if 'name' not in arg:
            return args.ReturnArg(arg['type'], doc)
        return self._get_arg(arg['name'], arg['type'], doc)

    def _get_arg(self, name, arg_type=None, doc=None):
        if name in self.args:
            return args.PositionalArg(name, arg_type, doc)
        elif name in self.kwargs:
            return args.OptionalArg(name, arg_type, doc, default=self.kwargs[name])
        elif name == self.keywords:
            return args.KeywordArg(name, doc)
        else:
            if not self.keywords:
                raise AttributeError('No argument {} in method {}:{}'.format(
                    name, inspect.getmodule(self._func).__name__, self._func.__name__))
            return args.OptionalArg(name, None, '')
